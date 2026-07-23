# Bilibili 装扮/收藏集素材下载器

一个用于搜索并下载 Bilibili 装扮或收藏集素材的工具，支持 CLI 命令行版本和 GUI 图形界面版本。

## 功能特性

### GUI 版本 (v2.0.0)

- 🖥️ **图形界面**：基于 PySide6 的现代化 GUI 界面
- 🔍 **搜索功能**：支持通过关键词搜索装扮或收藏集
- 📋 **搜索结果**：清晰展示搜索结果列表，支持查看详情
- 📦 **资源选择**：支持选择下载资源类型（表情包、封面等）
- ⬇️ **下载管理**：支持全部下载和选择下载两种模式
- 📊 **下载状态**：实时显示下载进度和状态（等待/下载中/已完成/失败）
- ⏸️ **暂停/继续**：支持暂停和继续下载任务
- 📁 **自定义路径**：默认下载到可执行文件所在目录，支持自定义路径

### CLI 版本 (v1.0.0)

- 🔍 **搜索功能**：支持通过关键词搜索装扮或收藏集
- 📦 **素材下载**：自动下载选中收藏集的所有图片资源
- 💾 **本地保存**：按收藏集名称创建文件夹，有序保存素材
- 🔄 **失败重试**：内置下载失败重试机制，提高下载成功率
- ⏱️ **指数退避**：智能延迟策略，避免频繁请求

## 使用方法

### GUI 版本

#### 方式一：直接运行可执行文件

1. 前往 [GitHub Releases](https://github.com/SnowDreamXUE/Bili-skin/releases) 页面下载最新版本的 `BiliGarbGUI.exe`
2. 将 `BiliGarbGUI.exe` 放到任意文件夹中
3. 双击运行即可（下载的文件会保存在 exe 所在目录）

#### 方式二：源码运行

```bash
cd gui_app
pip install -r requirements.txt
python main.py
```

#### 打包命令

```bash
cd gui_app
pyinstaller gui_app.spec --distpath "dist" --workpath "build"
```

### CLI 版本

#### 环境要求

- Python 3.6+
- `requests` 库

#### 安装依赖

```bash
pip install requests
```

#### 运行脚本

```bash
cd cli
python bilibili_garb_downloader.py
```

## 项目结构

```
.
├── cli/                            # CLI 版本
│   ├── bilibili_garb_downloader.py  # CLI 主程序
│   ├── bilibili_garb_downloader.spec # CLI 打包配置
│   ├── icon.ico                    # CLI 图标
│   └── version_info.txt            # CLI 版本信息
├── gui_app/                        # GUI 版本
│   ├── config/                     # 配置文件
│   │   ├── api.py                  # API 配置
│   │   └── style.py                # 样式配置
│   ├── core/                       # 核心模块
│   │   ├── api_client.py           # API 客户端
│   │   └── downloader.py           # 下载器
│   ├── ui/                         # UI 模块
│   │   ├── main_window.py          # 主窗口
│   │   ├── search_page.py          # 搜索页面
│   │   ├── result_page.py          # 搜索结果页面
│   │   ├── download_page.py        # 下载管理页面
│   │   └── threads.py              # 线程模块
│   ├── icon.ico                    # GUI 图标
│   ├── gui_app.spec                # GUI 打包配置
│   ├── main.py                     # GUI 入口文件
│   └── version_info.txt            # GUI 版本信息 (v2.0.0)
├── 装扮信息 API.md                 # 装扮相关 API 文档
├── 收藏集信息 API.md               # 收藏集相关 API 文档
├── 收藏集、装扮搜索 API.md         # 搜索相关 API 文档
└── README.md                       # 项目说明文档
```

## API 说明

本项目使用的 Bilibili API 接口文档详见项目中的 `.md` 文件：

- `装扮信息 API.md` - 装扮详情相关接口
- `收藏集信息 API.md` - 收藏集详情相关接口
- `收藏集、装扮搜索 API.md` - 搜索相关接口

## 注意事项

- 本工具仅供学习交流使用，请勿用于商业用途
- 下载的素材版权归 Bilibili 及原作者所有
- 请合理使用接口，避免频繁请求造成服务器压力

## 版本历史

### GUI v2.0.0

- 新增图形界面版本
- 支持资源类型选择下载
- 支持全部下载和选择下载模式
- 支持暂停/继续下载
- 默认下载路径为可执行文件所在目录

### CLI v1.0.0

- 初始版本
- 支持搜索和下载功能
- 支持失败重试机制

## 鸣谢

本项目 API 接口参考自以下开源项目，特此鸣谢：

- **[bilibili-API-collect](https://github.com/SocialSisterYi/bilibili-API-collect)** by SocialSisterYi

感谢作者对 Bilibili API 的整理和分享，为项目开发提供了重要参考。
