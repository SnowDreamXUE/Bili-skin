import os
import re
import time
from typing import Optional, Dict, Callable, List

import requests

from gui_app.config.api import HEADERS
from gui_app.core.api_client import ApiClient


class Downloader:
    SUIT_RESOURCE_TYPES = {
        "card": "动态卡片",
        "emoji_package": "表情包",
        "card_bg": "评论装扮",
        "thumbup": "点赞特效",
        "loading": "加载动画",
        "play_icon": "进度条",
        "skin": "个性主题",
        "space_bg": "空间海报"
    }

    COLLECTIBLE_RESOURCE_TYPES = {
        "card_img": "卡片图片",
        "video_list": "卡片视频",
        "cover": "封面"
    }

    def __init__(self):
        self._is_running = True
        self._is_paused = False

    def pause(self):
        self._is_paused = True

    def resume(self):
        self._is_paused = False

    def stop(self):
        self._is_running = False

    def _check_paused(self):
        while self._is_paused and self._is_running:
            time.sleep(0.1)

    def download_file(self, url: str, save_path: str) -> bool:
        if not self._is_running:
            return False
        try:
            resp = requests.get(url, headers=HEADERS, timeout=60, stream=True)
            resp.raise_for_status()
            total_size = int(resp.headers.get("content-length", 0))
            downloaded = 0
            with open(save_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if not self._is_running:
                        return False
                    self._check_paused()
                    f.write(chunk)
                    downloaded += len(chunk)
            return True
        except Exception as e:
            if os.path.exists(save_path):
                try:
                    os.remove(save_path)
                except:
                    pass
            raise Exception(f"下载失败 {url}: {e}")

    @staticmethod
    def sanitize_filename(name: str) -> str:
        illegal_chars = r'[<>:"/\\|？*]'
        name = re.sub(illegal_chars, "_", name)
        name = name.strip().strip(".")
        if len(name) > 200:
            name = name[:200]
        return name

    def download_collectible(self, name: str, act_id: int, lottery_id: int, base_dir: str,
                             progress_callback=None, log_callback=None,
                             pause_check_callback: Callable = None,
                             resource_types: List[str] = None) -> int:
        if log_callback:
            log_callback(f"正在获取收藏集详情：{name}")

        detail = ApiClient.get_dlc_detail(act_id, lottery_id)
        if not detail:
            raise Exception("无法获取收藏集详情")

        if resource_types is None:
            resource_types = list(self.COLLECTIBLE_RESOURCE_TYPES.keys())

        collect_dir = os.path.join(base_dir, "收藏集", self.sanitize_filename(name))
        os.makedirs(collect_dir, exist_ok=True)

        if "cover" in resource_types:
            cover_url = detail.get("cover", "")
            if cover_url:
                cover_ext = os.path.splitext(cover_url.split("?")[0])[1] or ".jpg"
                cover_path = os.path.join(collect_dir, f"cover{cover_ext}")
                if self.download_file(cover_url, cover_path):
                    if log_callback:
                        log_callback(f"✓ 封面：cover{cover_ext}")

        item_list = detail.get("item_list", [])
        if not item_list:
            if log_callback:
                log_callback("该收藏集没有可下载的卡片")
            return 0

        downloaded_count = 0
        total_items = len(item_list)

        for i, item in enumerate(item_list):
            if not self._is_running:
                break
            if pause_check_callback:
                pause_check_callback()
            card_info = item.get("card_info", {})
            if not card_info:
                continue

            card_name = card_info.get("card_name", "未知卡片")
            card_name = self.sanitize_filename(card_name)

            if "card_img" in resource_types:
                card_img = card_info.get("card_img")
                if card_img:
                    img_ext = os.path.splitext(card_img.split("?")[0])[1] or ".png"
                    img_path = os.path.join(collect_dir, f"{card_name}{img_ext}")
                    if self.download_file(card_img, img_path):
                        if log_callback:
                            log_callback(f"✓ 卡片图片：{card_name}")
                        downloaded_count += 1

            if "video_list" in resource_types:
                video_list = card_info.get("video_list", [])
                if video_list:
                    video_url = video_list[0]
                    video_ext = os.path.splitext(video_url.split("?")[0])[1] or ".mp4"
                    video_path = os.path.join(collect_dir, f"{card_name}{video_ext}")
                    if self.download_file(video_url, video_path):
                        if log_callback:
                            log_callback(f"✓ 卡片视频：{card_name}")
                        downloaded_count += 1

            if progress_callback:
                overall_percent = int(((i + 1) / total_items) * 100)
                progress_callback(overall_percent, f"正在处理 {card_name}...")

        if log_callback:
            log_callback(f"\n收藏集下载完成，共下载 {downloaded_count} 个文件")
        return downloaded_count

    def download_suit(self, name: str, item_id: int, base_dir: str,
                      progress_callback=None, log_callback=None,
                      pause_check_callback: Callable = None,
                      resource_types: List[str] = None) -> int:
        if log_callback:
            log_callback(f"正在获取装扮详情：{name}")

        detail = ApiClient.get_suit_detail(item_id)
        if not detail:
            raise Exception("无法获取装扮详情")

        if resource_types is None:
            resource_types = list(self.SUIT_RESOURCE_TYPES.keys())

        suit_items = detail.get("suit_items", {})
        if not suit_items:
            if log_callback:
                log_callback("该装扮没有可下载的素材")
            return 0

        suit_dir = os.path.join(base_dir, "装扮", self.sanitize_filename(name))
        os.makedirs(suit_dir, exist_ok=True)

        downloaded_count = 0
        total_files = 0

        resource_count_map = {}
        for resource_type in resource_types:
            items = suit_items.get(resource_type, [])
            if resource_type == "emoji_package":
                for emoji_item in items:
                    emoji_items = emoji_item.get("items", [])
                    resource_count_map[resource_type] = resource_count_map.get(resource_type, 0) + len(emoji_items)
            elif resource_type == "space_bg":
                for bg_item in items:
                    props = bg_item.get("properties", {})
                    image_pairs = {}
                    for key, value in props.items():
                        if not value:
                            continue
                        match = re.match(r'image(\d+)_(landscape|portrait)', key)
                        if match:
                            num = match.group(1)
                            if num not in image_pairs:
                                image_pairs[num] = 0
                            image_pairs[num] += 1
                    resource_count_map[resource_type] = resource_count_map.get(resource_type, 0) + sum(image_pairs.values())
            elif resource_type == "skin":
                resource_count_map[resource_type] = resource_count_map.get(resource_type, 0) + len(items) * 3
            else:
                resource_count_map[resource_type] = resource_count_map.get(resource_type, 0) + len(items)

        total_files = sum(resource_count_map.values())
        current_file = 0

        if "card" in resource_types and suit_items.get("card"):
            card_dir = os.path.join(suit_dir, "动态卡片")
            os.makedirs(card_dir, exist_ok=True)

            for card_item in suit_items["card"]:
                if not self._is_running:
                    break
                if pause_check_callback:
                    pause_check_callback()
                card_name = card_item.get("name", "未知卡片")
                card_name = self.sanitize_filename(card_name)

                props = card_item.get("properties", {})
                image_url = props.get("image")
                if image_url:
                    img_ext = os.path.splitext(image_url.split("?")[0])[1] or ".png"
                    img_path = os.path.join(card_dir, f"{card_name}{img_ext}")
                    if self.download_file(image_url, img_path):
                        if log_callback:
                            log_callback(f"✓ 动态卡片：{card_name}")
                        downloaded_count += 1

                fans_image = props.get("fans_image")
                if fans_image:
                    img_ext = os.path.splitext(fans_image.split("?")[0])[1] or ".png"
                    img_path = os.path.join(card_dir, f"{card_name}_fans{img_ext}")
                    if self.download_file(fans_image, img_path):
                        if log_callback:
                            log_callback(f"✓ 动态卡片粉丝图：{card_name}")
                        downloaded_count += 1

                current_file += 1
                if progress_callback:
                    overall_percent = int((current_file / total_files) * 100)
                    progress_callback(overall_percent, f"正在处理动态卡片 {card_name}...")

        if "emoji_package" in resource_types and suit_items.get("emoji_package"):
            emoji_dir = os.path.join(suit_dir, "表情包")
            os.makedirs(emoji_dir, exist_ok=True)

            for emoji_item in suit_items["emoji_package"]:
                items = emoji_item.get("items", [])
                for item in items:
                    if not self._is_running:
                        break
                    if pause_check_callback:
                        pause_check_callback()
                    item_name = item.get("name", "")
                    match = re.match(r'\[.*?_(.*?)\]', item_name)
                    if match:
                        emoji_name = match.group(1)
                    else:
                        emoji_name = item_name
                    emoji_name = self.sanitize_filename(emoji_name)

                    img_url = item.get("properties", {}).get("image")
                    if img_url:
                        img_ext = os.path.splitext(img_url.split("?")[0])[1] or ".png"
                        img_path = os.path.join(emoji_dir, f"{emoji_name}{img_ext}")
                        if self.download_file(img_url, img_path):
                            if log_callback:
                                log_callback(f"✓ 表情包：{emoji_name}")
                            downloaded_count += 1
                    current_file += 1
                    if progress_callback:
                        overall_percent = int((current_file / total_files) * 100)
                        progress_callback(overall_percent, f"正在处理表情包 {emoji_name}...")

        if "card_bg" in resource_types and suit_items.get("card_bg"):
            card_bg_dir = os.path.join(suit_dir, "评论装扮")
            os.makedirs(card_bg_dir, exist_ok=True)

            for bg_item in suit_items["card_bg"]:
                if not self._is_running:
                    break
                if pause_check_callback:
                    pause_check_callback()
                bg_name = bg_item.get("name", "未知背景")
                bg_name = self.sanitize_filename(bg_name)

                props = bg_item.get("properties", {})
                image_url = props.get("image")
                if image_url:
                    img_ext = os.path.splitext(image_url.split("?")[0])[1] or ".png"
                    img_path = os.path.join(card_bg_dir, f"{bg_name}{img_ext}")
                    if self.download_file(image_url, img_path):
                        if log_callback:
                            log_callback(f"✓ 评论装扮：{bg_name}")
                        downloaded_count += 1

                current_file += 1
                if progress_callback:
                    overall_percent = int((current_file / total_files) * 100)
                    progress_callback(overall_percent, f"正在处理评论装扮 {bg_name}...")

        if "thumbup" in resource_types and suit_items.get("thumbup"):
            thumbup_dir = os.path.join(suit_dir, "点赞特效")
            os.makedirs(thumbup_dir, exist_ok=True)

            for thumbup_item in suit_items["thumbup"]:
                if not self._is_running:
                    break
                if pause_check_callback:
                    pause_check_callback()
                thumbup_name = thumbup_item.get("name", "未知特效")
                thumbup_name = self.sanitize_filename(thumbup_name)

                props = thumbup_item.get("properties", {})
                image_url = props.get("image")
                if image_url:
                    img_ext = os.path.splitext(image_url.split("?")[0])[1] or ".png"
                    img_path = os.path.join(thumbup_dir, f"{thumbup_name}{img_ext}")
                    if self.download_file(image_url, img_path):
                        if log_callback:
                            log_callback(f"✓ 点赞特效：{thumbup_name}")
                        downloaded_count += 1

                current_file += 1
                if progress_callback:
                    overall_percent = int((current_file / total_files) * 100)
                    progress_callback(overall_percent, f"正在处理点赞特效 {thumbup_name}...")

        if "loading" in resource_types and suit_items.get("loading"):
            loading_dir = os.path.join(suit_dir, "加载动画")
            os.makedirs(loading_dir, exist_ok=True)

            for loading_item in suit_items["loading"]:
                if not self._is_running:
                    break
                if pause_check_callback:
                    pause_check_callback()
                loading_name = loading_item.get("name", "未知加载动画")
                loading_name = self.sanitize_filename(loading_name)

                props = loading_item.get("properties", {})
                loading_url = props.get("loading_url")
                if loading_url:
                    ext = os.path.splitext(loading_url.split("?")[0])[1] or ".webp"
                    file_path = os.path.join(loading_dir, f"{loading_name}{ext}")
                    if self.download_file(loading_url, file_path):
                        if log_callback:
                            log_callback(f"✓ 加载动画：{loading_name}")
                        downloaded_count += 1

                loading_frame_url = props.get("loading_frame_url")
                if loading_frame_url:
                    ext = os.path.splitext(loading_frame_url.split("?")[0])[1] or ".png"
                    file_path = os.path.join(loading_dir, f"{loading_name}_frame{ext}")
                    if self.download_file(loading_frame_url, file_path):
                        if log_callback:
                            log_callback(f"✓ 加载动画帧：{loading_name}")
                        downloaded_count += 1

                current_file += 1
                if progress_callback:
                    overall_percent = int((current_file / total_files) * 100)
                    progress_callback(overall_percent, f"正在处理加载动画 {loading_name}...")

        if "play_icon" in resource_types and suit_items.get("play_icon"):
            play_icon_dir = os.path.join(suit_dir, "进度条")
            os.makedirs(play_icon_dir, exist_ok=True)

            for play_icon_item in suit_items["play_icon"]:
                if not self._is_running:
                    break
                if pause_check_callback:
                    pause_check_callback()
                play_icon_name = play_icon_item.get("name", "未知进度条")
                play_icon_name = self.sanitize_filename(play_icon_name)

                props = play_icon_item.get("properties", {})
                for key, value in props.items():
                    if not value or not isinstance(value, str) or not value.startswith("http"):
                        continue
                    ext = os.path.splitext(value.split("?")[0])[1] or ".png"
                    file_path = os.path.join(play_icon_dir, f"{play_icon_name}_{key}{ext}")
                    if self.download_file(value, file_path):
                        if log_callback:
                            log_callback(f"✓ 进度条{key}：{play_icon_name}")
                        downloaded_count += 1

                current_file += 1
                if progress_callback:
                    overall_percent = int((current_file / total_files) * 100)
                    progress_callback(overall_percent, f"正在处理进度条 {play_icon_name}...")

        if "skin" in resource_types and suit_items.get("skin"):
            skin_dir = os.path.join(suit_dir, "个性主题")
            os.makedirs(skin_dir, exist_ok=True)

            for skin_item in suit_items["skin"]:
                if not self._is_running:
                    break
                if pause_check_callback:
                    pause_check_callback()
                skin_name = skin_item.get("name", "未知主题")
                skin_name = self.sanitize_filename(skin_name)

                props = skin_item.get("properties", {})
                for key, value in props.items():
                    if not value or not isinstance(value, str) or not value.startswith("http"):
                        continue
                    ext = os.path.splitext(value.split("?")[0])[1] or ".png"
                    file_path = os.path.join(skin_dir, f"{skin_name}_{key}{ext}")
                    if self.download_file(value, file_path):
                        if log_callback:
                            log_callback(f"✓ 个性主题{key}：{skin_name}")
                        downloaded_count += 1

                current_file += 1
                if progress_callback:
                    overall_percent = int((current_file / total_files) * 100)
                    progress_callback(overall_percent, f"正在处理个性主题 {skin_name}...")

        if "space_bg" in resource_types and suit_items.get("space_bg"):
            bg_dir = os.path.join(suit_dir, "空间海报")
            os.makedirs(bg_dir, exist_ok=True)

            for bg_item in suit_items["space_bg"]:
                if not self._is_running:
                    break
                if pause_check_callback:
                    pause_check_callback()
                props = bg_item.get("properties", {})
                image_pairs = {}
                for key, value in props.items():
                    if not value:
                        continue
                    match = re.match(r'image(\d+)_(landscape|portrait)', key)
                    if match:
                        num = match.group(1)
                        orientation = match.group(2)
                        if num not in image_pairs:
                            image_pairs[num] = {}
                        image_pairs[num][orientation] = value

                for num, orientations in sorted(image_pairs.items(), key=lambda x: int(x[0])):
                    if not self._is_running:
                        break
                    if pause_check_callback:
                        pause_check_callback()
                    base_name = f"{self.sanitize_filename(name)}_{num}"

                    if "landscape" in orientations:
                        img_url = orientations["landscape"]
                        img_ext = os.path.splitext(img_url.split("?")[0])[1] or ".jpg"
                        img_path = os.path.join(bg_dir, f"{base_name}_landscape{img_ext}")
                        if self.download_file(img_url, img_path):
                            if log_callback:
                                log_callback(f"✓ 空间海报横版：{base_name}")
                            downloaded_count += 1
                        current_file += 1
                        if progress_callback:
                            overall_percent = int((current_file / total_files) * 100)
                            progress_callback(overall_percent, f"正在处理空间海报 {base_name}_landscape...")

                    if "portrait" in orientations:
                        img_url = orientations["portrait"]
                        img_ext = os.path.splitext(img_url.split("?")[0])[1] or ".jpg"
                        img_path = os.path.join(bg_dir, f"{base_name}_portrait{img_ext}")
                        if self.download_file(img_url, img_path):
                            if log_callback:
                                log_callback(f"✓ 空间海报竖版：{base_name}")
                            downloaded_count += 1
                        current_file += 1
                        if progress_callback:
                            overall_percent = int((current_file / total_files) * 100)
                            progress_callback(overall_percent, f"正在处理空间海报 {base_name}_portrait...")

        if log_callback:
            log_callback(f"\n装扮下载完成，共下载 {downloaded_count} 个文件")
        return downloaded_count