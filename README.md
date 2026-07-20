# Bilibili 装扮/收藏集素材下载器

一个用于搜索并下载 Bilibili 装扮或收藏集素材的 Python 脚本。

## 功能特性

- 🔍 **搜索功能**：支持通过关键词搜索装扮或收藏集
- 📦 **素材下载**：自动下载选中收藏集的所有图片资源
- 💾 **本地保存**：按收藏集名称创建文件夹，有序保存素材
- 🔄 **失败重试**：内置下载失败重试机制，提高下载成功率
- ⏱️ **指数退避**：智能延迟策略，避免频繁请求

## 使用方法

### 环境要求

- Python 3.6+
- `requests` 库

### 安装依赖

```bash
pip install requests
```

### 运行脚本

```bash
python bilibili_garb_downloader.py
```

### 使用流程

1. 运行脚本后，输入要搜索的装扮或收藏集关键词
2. 从搜索结果列表中选择想要的收藏集（输入对应序号）
3. 脚本会自动在当前目录下创建以收藏集命名的文件夹
4. 所有相关素材图片将下载到该文件夹中

## 项目结构

```
.
├── bilibili_garb_downloader.py    # 主程序脚本
├── README.md                       # 项目说明文档
├── 装扮信息 API.md                 # 装扮相关 API 文档
├── 收藏集信息 API.md               # 收藏集相关 API 文档
└── 收藏集、装扮搜索 API.md         # 搜索相关 API 文档
```

## API 说明

本项目使用的 Bilibili API 接口文档详见项目中的 `.md` 文件：

- `装扮信息 API.md` - 装扮详情相关接口
- `收藏集信息 API.md` - 收藏集详情相关接口
- `收藏集、装扮搜索 API.md` - 搜索相关接口

## 注意事项

- 本脚本仅供学习交流使用，请勿用于商业用途
- 下载的素材版权归 Bilibili 及原作者所有
- 请合理使用接口，避免频繁请求造成服务器压力

## 鸣谢

本项目 API 接口参考自以下开源项目，特此鸣谢：

- **[bilibili-API-collect](https://github.com/SocialSisterYi/bilibili-API-collect)** by SocialSisterYi

感谢作者对 Bilibili API 的整理和分享，为项目开发提供了重要参考。