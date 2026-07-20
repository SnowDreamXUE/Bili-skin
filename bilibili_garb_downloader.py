#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bilibili 装扮/收藏集素材下载脚本
支持搜索装扮或收藏集名称，选择并下载对应素材
"""

import os
import re
import sys
import json
import requests
from typing import Optional


# API 端点
SEARCH_API = "https://api.bilibili.com/x/garb/v2/mall/home/search"
SUIT_DETAIL_API = "https://api.bilibili.com/x/garb/v2/mall/suit/detail"
DLC_DETAIL_API = "https://api.bilibili.com/x/vas/dlc_act/lottery_home_detail"

# 请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.bilibili.com/",
}


def search_items(keyword: str, ps: int = 20) -> list:
    """搜索装扮或收藏集"""
    params = {
        "key_word": keyword,
        "ps": ps,
        "pn": 1,
    }
    try:
        resp = requests.get(SEARCH_API, params=params, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") == 0 and data.get("data", {}).get("list"):
            return data["data"]["list"]
        return []
    except Exception as e:
        print(f"搜索失败：{e}")
        return []


def get_suit_detail(item_id: int) -> Optional[dict]:
    """获取装扮详情"""
    params = {"item_id": item_id}
    try:
        resp = requests.get(SUIT_DETAIL_API, params=params, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") == 0:
            return data.get("data")
        return None
    except Exception as e:
        print(f"获取装扮详情失败：{e}")
        return None


def get_dlc_detail(act_id: int, lottery_id: int) -> Optional[dict]:
    """获取收藏集详情"""
    params = {"act_id": act_id, "lottery_id": lottery_id}
    try:
        resp = requests.get(DLC_DETAIL_API, params=params, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") == 0:
            return data.get("data")
        return None
    except Exception as e:
        print(f"获取收藏集详情失败：{e}")
        return None


def download_file(url: str, save_path: str) -> bool:
    """下载文件"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=60, stream=True)
        resp.raise_for_status()
        with open(save_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"下载失败 {url}: {e}")
        return False


def sanitize_filename(name: str) -> str:
    """清理文件名中的非法字符"""
    # 移除 Windows 文件名非法字符
    illegal_chars = r'[<>:"/\\|？*]'
    name = re.sub(illegal_chars, "_", name)
    # 移除前后空格和点
    name = name.strip().strip(".")
    # 限制长度
    if len(name) > 200:
        name = name[:200]
    return name


def download_collectible(name: str, act_id: int, lottery_id: int, base_dir: str):
    """下载收藏集素材（卡片图片和视频）"""
    print(f"\n正在获取收藏集详情：{name}")
    
    detail = get_dlc_detail(act_id, lottery_id)
    if not detail:
        print("无法获取收藏集详情")
        return
    
    # 创建收藏集文件夹
    collect_dir = os.path.join(base_dir, "收藏集", sanitize_filename(name))
    os.makedirs(collect_dir, exist_ok=True)
    
    item_list = detail.get("item_list", [])
    if not item_list:
        print("该收藏集没有可下载的卡片")
        return
    
    downloaded_count = 0
    for item in item_list:
        card_info = item.get("card_info", {})
        if not card_info:
            continue
        
        card_name = card_info.get("card_name", "未知卡片")
        card_name = sanitize_filename(card_name)
        
        # 下载卡片图片（使用无水印版本）
        card_img = card_info.get("card_img")
        if card_img:
            img_ext = os.path.splitext(card_img.split("?")[0])[1] or ".png"
            img_path = os.path.join(collect_dir, f"{card_name}{img_ext}")
            if download_file(card_img, img_path):
                print(f"  ✓ 卡片图片：{card_name}")
                downloaded_count += 1
        
        # 下载卡片视频（取第一个链接）
        video_list = card_info.get("video_list", [])
        if video_list:
            video_url = video_list[0]
            video_ext = os.path.splitext(video_url.split("?")[0])[1] or ".mp4"
            video_path = os.path.join(collect_dir, f"{card_name}{video_ext}")
            if download_file(video_url, video_path):
                print(f"  ✓ 卡片视频：{card_name}")
                downloaded_count += 1
    
    print(f"\n收藏集下载完成，共下载 {downloaded_count} 个文件")


def download_suit(name: str, item_id: int, base_dir: str):
    """下载装扮素材（表情包和背景图）"""
    print(f"\n正在获取装扮详情：{name}")
    
    detail = get_suit_detail(item_id)
    if not detail:
        print("无法获取装扮详情")
        return
    
    suit_items = detail.get("suit_items", {})
    if not suit_items:
        print("该装扮没有可下载的素材")
        return
    
    # 创建装扮文件夹
    suit_dir = os.path.join(base_dir, "装扮", sanitize_filename(name))
    os.makedirs(suit_dir, exist_ok=True)
    
    downloaded_count = 0
    
    # 下载表情包
    emoji_package = suit_items.get("emoji_package", [])
    if emoji_package:
        emoji_dir = os.path.join(suit_dir, "表情包")
        os.makedirs(emoji_dir, exist_ok=True)
        
        for emoji_item in emoji_package:
            items = emoji_item.get("items", [])
            for item in items:
                item_name = item.get("name", "")
                # 清理名称，去掉 [装扮名_] 前缀
                match = re.match(r'\[.*?_(.*?)\]', item_name)
                if match:
                    emoji_name = match.group(1)
                else:
                    emoji_name = item_name
                emoji_name = sanitize_filename(emoji_name)
                
                img_url = item.get("properties", {}).get("image")
                if img_url:
                    img_ext = os.path.splitext(img_url.split("?")[0])[1] or ".png"
                    img_path = os.path.join(emoji_dir, f"{emoji_name}{img_ext}")
                    if download_file(img_url, img_path):
                        print(f"  ✓ 表情包：{emoji_name}")
                        downloaded_count += 1
    
    # 下载背景图
    space_bg = suit_items.get("space_bg", [])
    if space_bg:
        bg_dir = os.path.join(suit_dir, "背景图")
        os.makedirs(bg_dir, exist_ok=True)
        
        for bg_item in space_bg:
            props = bg_item.get("properties", {})
            
            # 提取所有 landscape 和 portrait 图片
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
            
            # 下载每对图片
            for num, orientations in sorted(image_pairs.items(), key=lambda x: int(x[0])):
                base_name = f"{sanitize_filename(name)}_{num}"
                
                # 下载横版
                if "landscape" in orientations:
                    img_url = orientations["landscape"]
                    img_ext = os.path.splitext(img_url.split("?")[0])[1] or ".jpg"
                    img_path = os.path.join(bg_dir, f"{base_name}_landscape{img_ext}")
                    if download_file(img_url, img_path):
                        print(f"  ✓ 背景图横版：{base_name}_landscape")
                        downloaded_count += 1
                
                # 下载竖版
                if "portrait" in orientations:
                    img_url = orientations["portrait"]
                    img_ext = os.path.splitext(img_url.split("?")[0])[1] or ".jpg"
                    img_path = os.path.join(bg_dir, f"{base_name}_portrait{img_ext}")
                    if download_file(img_url, img_path):
                        print(f"  ✓ 背景图竖版：{base_name}_portrait")
                        downloaded_count += 1
    
    print(f"\n装扮下载完成，共下载 {downloaded_count} 个文件")


def select_item(items: list) -> Optional[dict]:
    """让用户选择要下载的项"""
    if not items:
        return None
    
    print("\n搜索结果:")
    print("-" * 80)
    
    for i, item in enumerate(items, 1):
        name = item.get("name", "未知")
        part_id = item.get("part_id", 0)
        item_type = "收藏集" if part_id == 0 else "装扮"
        properties = item.get("properties", {})
        cover = properties.get("image_cover", "")
        
        print(f"{i}. [{item_type}] {name}")
        if cover:
            print(f"   封面：{cover[:60]}...")
    
    print("-" * 80)
    
    while True:
        try:
            choice = input(f"请选择要下载的项 (1-{len(items)})，或输入 q 退出：").strip()
            if choice.lower() == 'q':
                return None
            
            idx = int(choice) - 1
            if 0 <= idx < len(items):
                return items[idx]
            else:
                print(f"请输入 1-{len(items)} 之间的数字")
        except ValueError:
            print("请输入有效的数字")


def main():
    """主函数"""
    print("=" * 60)
    print("Bilibili 装扮/收藏集素材下载工具")
    print("=" * 60)
    
    # 获取当前脚本目录作为基础目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if not base_dir:
        base_dir = os.getcwd()
    
    print(f"素材将保存在：{base_dir}")
    print()
    
    while True:
        keyword = input("请输入搜索关键词（装扮或收藏集名称），或输入 q 退出：").strip()
        if keyword.lower() == 'q':
            print("再见！")
            break
        
        if not keyword:
            print("关键词不能为空")
            continue
        
        print(f"\n正在搜索：{keyword}...")
        items = search_items(keyword)
        
        if not items:
            print("未找到相关结果，请尝试其他关键词")
            continue
        
        selected = select_item(items)
        if not selected:
            continue
        
        name = selected.get("name", "未知")
        part_id = selected.get("part_id", 0)
        properties = selected.get("properties", {})
        
        if part_id == 0:
            # 收藏集
            act_id = properties.get("dlc_act_id")
            lottery_id = properties.get("dlc_lottery_id")
            
            if not act_id or not lottery_id:
                print("无法获取收藏集的 act_id 或 lottery_id")
                continue
            
            print(f"\n准备下载收藏集：{name}")
            print(f"  act_id: {act_id}")
            print(f"  lottery_id: {lottery_id}")
            
            confirm = input("确认下载？(y/n): ").strip().lower()
            if confirm != 'y':
                continue
            
            download_collectible(name, int(act_id), int(lottery_id), base_dir)
        
        else:
            # 装扮
            item_id = selected.get("item_id")
            
            if not item_id:
                print("无法获取装扮的 item_id")
                continue
            
            print(f"\n准备下载装扮：{name}")
            print(f"  item_id: {item_id}")
            
            confirm = input("确认下载？(y/n): ").strip().lower()
            if confirm != 'y':
                continue
            
            download_suit(name, int(item_id), base_dir)
        
        print("\n" + "=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断操作")
        sys.exit(0)
    except Exception as e:
        print(f"\n发生错误：{e}")
        sys.exit(1)
