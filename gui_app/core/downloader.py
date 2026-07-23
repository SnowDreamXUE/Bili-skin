import os
import re
import time
from typing import Optional, Dict, Callable

import requests

from gui_app.config.api import HEADERS
from gui_app.core.api_client import ApiClient


class Downloader:
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
                             pause_check_callback: Callable = None) -> int:
        if log_callback:
            log_callback(f"正在获取收藏集详情：{name}")

        detail = ApiClient.get_dlc_detail(act_id, lottery_id)
        if not detail:
            raise Exception("无法获取收藏集详情")

        collect_dir = os.path.join(base_dir, "收藏集", self.sanitize_filename(name))
        os.makedirs(collect_dir, exist_ok=True)

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

            card_img = card_info.get("card_img")
            if card_img:
                img_ext = os.path.splitext(card_img.split("?")[0])[1] or ".png"
                img_path = os.path.join(collect_dir, f"{card_name}{img_ext}")
                if self.download_file(card_img, img_path):
                    if log_callback:
                        log_callback(f"✓ 卡片图片：{card_name}")
                    downloaded_count += 1

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
                      pause_check_callback: Callable = None) -> int:
        if log_callback:
            log_callback(f"正在获取装扮详情：{name}")

        detail = ApiClient.get_suit_detail(item_id)
        if not detail:
            raise Exception("无法获取装扮详情")

        suit_items = detail.get("suit_items", {})
        if not suit_items:
            if log_callback:
                log_callback("该装扮没有可下载的素材")
            return 0

        suit_dir = os.path.join(base_dir, "装扮", self.sanitize_filename(name))
        os.makedirs(suit_dir, exist_ok=True)

        downloaded_count = 0
        total_files = 0

        emoji_package = suit_items.get("emoji_package", [])
        space_bg = suit_items.get("space_bg", [])

        for emoji_item in emoji_package:
            items = emoji_item.get("items", [])
            total_files += len(items)

        for bg_item in space_bg:
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
            total_files += sum(image_pairs.values())

        current_file = 0

        if emoji_package:
            emoji_dir = os.path.join(suit_dir, "表情包")
            os.makedirs(emoji_dir, exist_ok=True)

            for emoji_item in emoji_package:
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

        if space_bg:
            bg_dir = os.path.join(suit_dir, "背景图")
            os.makedirs(bg_dir, exist_ok=True)

            for bg_item in space_bg:
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
                                log_callback(f"✓ 背景图横版：{base_name}_landscape")
                            downloaded_count += 1
                        current_file += 1
                        if progress_callback:
                            overall_percent = int((current_file / total_files) * 100)
                            progress_callback(overall_percent, f"正在处理背景图 {base_name}_landscape...")

                    if "portrait" in orientations:
                        img_url = orientations["portrait"]
                        img_ext = os.path.splitext(img_url.split("?")[0])[1] or ".jpg"
                        img_path = os.path.join(bg_dir, f"{base_name}_portrait{img_ext}")
                        if self.download_file(img_url, img_path):
                            if log_callback:
                                log_callback(f"✓ 背景图竖版：{base_name}_portrait")
                            downloaded_count += 1
                        current_file += 1
                        if progress_callback:
                            overall_percent = int((current_file / total_files) * 100)
                            progress_callback(overall_percent, f"正在处理背景图 {base_name}_portrait...")

        if log_callback:
            log_callback(f"\n装扮下载完成，共下载 {downloaded_count} 个文件")
        return downloaded_count