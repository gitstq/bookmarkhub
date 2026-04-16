<div align="center">

# 🌐 BookmarkHub

**多平台书签收集、搜索、分类与导出 CLI 工具**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-20%20passed-brightgreen.svg)]()

[English](#english) · [繁體中文](#繁體中文) · [日本語](#日本語)

从 HackerNews、Reddit、GitHub Trending、Lobste.rs 一键同步书签到本地，配合全文搜索、智能标签、多格式导出，打造你的专属知识金库 🏦

</div>

---

## 🎉 项目介绍

每天在 HackerNews、Reddit、GitHub 上刷到好内容，随手收藏然后……再也找不到了？😕

**BookmarkHub** 就是为你打造的命令行书签管理工具：

- 🔄 **多平台一键同步** — 支持 HackerNews、Reddit、GitHub Trending、Lobste.rs，一条命令拉取所有收藏
- 🔍 **本地全文搜索** — 基于 SQLite FTS5，毫秒级检索，所有数据都在你本地
- 🏷️ **智能自动标签** — 根据内容关键词自动分类（编程、AI、安全、前端……）
- 📤 **多格式导出** — Markdown / JSON / HTML（自带搜索） / EPUB，随你选择
- ➕ **手动添加** — 随时保存任意网页链接
- 🎨 **彩色终端 UI** — Rich 驱动，表格、状态栏、进度提示一应俱全

**差异化亮点**：灵感来源于 [fieldtheory-cli](https://github.com/afar1/fieldtheory-cli)（Twitter 书签同步工具），但做了全面升级——不限于单一平台，支持 4 大技术社区同步、本地全文检索、智能标签分类、4 种格式导出，打造完整书签管理闭环。

## ✨ 核心特性

- 🌐 **多平台同步** — HackerNews / Reddit / GitHub Trending / Lobste.rs 一键采集
- 🔍 **FTS5 全文搜索** — 毫秒级本地检索，支持标题、描述、标签跨字段搜索
- 🏷️ **智能自动标签** — 关键词触发自动分类（programming / ai / security / devops / data / design / frontend）
- 📤 **四格式导出** — Markdown、JSON、HTML（自带搜索 UI）、EPUB（电子书格式）
- 🔄 **增量同步** — 已有书签自动跳过，只入库新内容
- 💾 **本地优先** — SQLite 存储，零云端依赖，数据完全由你掌控
- 🎨 **彩色终端** — Rich 驱动的表格、状态栏、彩色输出
- 📊 **统计面板** — 按来源、标签维度查看书签分布
- 🪶 **轻量依赖** — 只依赖 click / rich / httpx / beautifulsoup4 四个核心包

## 🚀 快速开始

### 环境要求

- Python 3.9+
- pip

### 安装

```bash
# 克隆仓库
git clone https://github.com/gitstq/bookmarkhub.git
cd bookmarkhub

# 安装依赖
pip install -e .
```

### 基础使用

```bash
# 同步 HackerNews 热门
bookmarkhub sync hackernews

# 同步 Reddit（指定子版块）
bookmarkhub sync reddit --subreddit programming

# 同步 GitHub Trending（按语言）
bookmarkhub sync github --language python --since weekly

# 一键同步所有平台
bookmarkhub sync-all

# 手动添加书签
bookmarkhub add https://example.com -t "Example Site" -T "web,reference"

# 全文搜索
bookmarkhub search "machine learning"

# 按标签筛选
bookmarkhub list --tag ai

# 查看统计
bookmarkhub stats

# 导出为 Markdown
bookmarkhub export markdown

# 导出为 HTML（自带搜索 UI）
bookmarkhub export html -o my-bookmarks.html

# 导出为 EPUB 电子书
bookmarkhub export epub -o my-bookmarks.epub
```

## 📖 详细使用指南

### 同步命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `sync hackernews` | 同步 HN 热门 | `bookmarkhub sync hackernews -l 50` |
| `sync reddit` | 同步 Reddit | `bookmarkhub sync reddit -s python` |
| `sync github` | 同步 GitHub Trending | `bookmarkhub sync github -L rust --since weekly` |
| `sync lobsters` | 同步 Lobste.rs | `bookmarkhub sync lobsters` |
| `sync-all` | 同步所有平台 | `bookmarkhub sync-all -l 20` |

### 搜索与筛选

```bash
# 全文搜索（标题 + 描述 + 标签）
bookmarkhub search "rust programming"

# 按来源筛选
bookmarkhub search "python" --source hackernews

# 列出所有书签
bookmarkhub list

# 按来源列出来
bookmarkhub list --source reddit

# 按标签筛选
bookmarkhub list --tag ai
```

### 导出格式

| 格式 | 说明 | 适用场景 |
|------|------|----------|
| `markdown` | Markdown 文档，按来源分组 | 笔记、博客、Obsidian |
| `json` | 结构化 JSON | 程序化处理、数据迁移 |
| `html` | 自带搜索 UI 的独立 HTML 页面 | 浏览器查看、分享 |
| `epub` | EPUB 电子书 | 电子阅读器、iPad |

### 智能自动标签规则

BookmarkHub 会根据书签内容自动打标签：

| 关键词 | 自动标签 |
|--------|----------|
| python, javascript, rust, golang | `programming` |
| react, vue, css, html | `frontend` |
| ai, llm, gpt, claude, machine learning | `ai` |
| security, hacking, vulnerability, cve | `security` |
| docker, kubernetes, ci/cd | `devops` |
| database, sql, postgres, mongodb | `data` |
| design, ui, ux | `design` |

你也可以手动添加标签，手动标签和自动标签会合并去重。

## 💡 设计思路与迭代规划

### 设计理念

- **本地优先** — 你的书签数据属于你，不存储在云端，不依赖第三方认证
- **增量同步** — 只添加新书签，不重复入库，避免数据膨胀
- **即搜即得** — FTS5 全文索引，输入即搜索，无需等待
- **零门槛上手** — HackerNews / Lobste.rs 无需认证即可同步

### 后续迭代计划

- [ ] 🐦 Twitter/X 书签同步（Cookie 认证）
- [ ] 🔖 Pocket / Instapaper 导入
- [ ] 📰 RSS 源订阅同步
- [ ] 🤖 LLM 驱动的智能摘要生成
- [ ] 🖥️ Web UI 仪表盘
- [ ] 🔗 书签链接健康检查
- [ ] 📱 TUI 交互界面（Textual）
- [ ] 🌍 更多平台：ProductHunt、Dev.to、Medium

### 贡献方向

欢迎贡献新的平台 Fetcher、导出格式、自动标签规则！详见 [贡献指南](#🤝-贡献指南)

## 📦 安装与部署

### 从源码安装

```bash
git clone https://github.com/gitstq/bookmarkhub.git
cd bookmarkhub
pip install -e .
```

### 开发环境

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

### 数据存储位置

- 数据库：`~/.bookmarkhub/bookmarks.db`（SQLite）
- 导出文件：`./exports/` 目录（默认）

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -m 'feat: add your feature'`
4. 推送分支：`git push origin feature/your-feature`
5. 提交 Pull Request

**提交规范**：遵循 [Angular 提交规范](https://github.com/angular/angular/blob/master/CONTRIBUTING.md#commit)

- `feat:` 新功能
- `fix:` 修复问题
- `docs:` 文档更新
- `refactor:` 代码重构
- `test:` 测试相关

**Issue 反馈**：请提供操作系统、Python 版本、完整错误信息

## 📄 开源协议

本项目基于 [MIT 协议](LICENSE) 开源，可自由使用、修改和分发。

---

<a id="english"></a>

# 🌐 BookmarkHub

**Multi-platform bookmark collector, searcher, organizer & exporter CLI**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-20%20passed-brightgreen.svg)]()

Sync bookmarks from HackerNews, Reddit, GitHub Trending, and Lobste.rs — all stored locally with full-text search, smart auto-tagging, and multi-format export. Your personal knowledge vault 🏦

## 🎉 Introduction

Bookmark great content on HackerNews, Reddit, GitHub every day, save it, and then… never find it again? 😕

**BookmarkHub** is the CLI bookmark manager built for you:

- 🔄 **One-click multi-platform sync** — HackerNews, Reddit, GitHub Trending, Lobste.rs
- 🔍 **Local full-text search** — SQLite FTS5, millisecond retrieval, all data stays on your machine
- 🏷️ **Smart auto-tagging** — Auto-classify by content keywords (programming, AI, security, frontend…)
- 📤 **Multi-format export** — Markdown / JSON / HTML (with built-in search) / EPUB
- ➕ **Manual additions** — Save any URL anytime
- 🎨 **Rich terminal UI** — Tables, spinners, colored output powered by Rich

**What makes it different**: Inspired by [fieldtheory-cli](https://github.com/afar1/fieldtheory-cli) (Twitter bookmark sync), but comprehensively upgraded — not limited to one platform, supports 4 major tech communities, local full-text search, smart tagging, and 4 export formats for a complete bookmark management workflow.

## ✨ Key Features

- 🌐 **Multi-platform sync** — HackerNews / Reddit / GitHub Trending / Lobste.rs
- 🔍 **FTS5 full-text search** — Millisecond local search across title, description, tags
- 🏷️ **Smart auto-tagging** — Keyword-triggered classification (programming / ai / security / devops / data / design / frontend)
- 📤 **Four export formats** — Markdown, JSON, HTML (with search UI), EPUB
- 🔄 **Incremental sync** — Existing bookmarks skipped, only new content added
- 💾 **Local-first** — SQLite storage, zero cloud dependency, you own your data
- 🎨 **Colorful terminal** — Rich-powered tables, spinners, colored output
- 📊 **Stats dashboard** — View bookmark distribution by source and tag
- 🪶 **Lightweight** — Only 4 core dependencies: click / rich / httpx / beautifulsoup4

## 🚀 Quick Start

### Requirements

- Python 3.9+
- pip

### Install

```bash
git clone https://github.com/gitstq/bookmarkhub.git
cd bookmarkhub
pip install -e .
```

### Basic Usage

```bash
# Sync from HackerNews
bookmarkhub sync hackernews

# Sync from Reddit (specific subreddit)
bookmarkhub sync reddit --subreddit programming

# Sync GitHub Trending (by language)
bookmarkhub sync github --language python --since weekly

# Sync all platforms at once
bookmarkhub sync-all

# Add a bookmark manually
bookmarkhub add https://example.com -t "Example Site" -T "web,reference"

# Full-text search
bookmarkhub search "machine learning"

# Filter by tag
bookmarkhub list --tag ai

# View stats
bookmarkhub stats

# Export as Markdown
bookmarkhub export markdown

# Export as HTML (with built-in search UI)
bookmarkhub export html -o my-bookmarks.html

# Export as EPUB e-book
bookmarkhub export epub -o my-bookmarks.epub
```

## 📖 Detailed Guide

### Sync Commands

| Command | Description | Example |
|---------|-------------|---------|
| `sync hackernews` | Sync HN top stories | `bookmarkhub sync hackernews -l 50` |
| `sync reddit` | Sync Reddit posts | `bookmarkhub sync reddit -s python` |
| `sync github` | Sync GitHub Trending | `bookmarkhub sync github -L rust --since weekly` |
| `sync lobsters` | Sync Lobste.rs stories | `bookmarkhub sync lobsters` |
| `sync-all` | Sync all platforms | `bookmarkhub sync-all -l 20` |

### Search & Filter

```bash
# Full-text search (title + description + tags)
bookmarkhub search "rust programming"

# Filter by source
bookmarkhub search "python" --source hackernews

# List all bookmarks
bookmarkhub list

# Filter by source
bookmarkhub list --source reddit

# Filter by tag
bookmarkhub list --tag ai
```

### Export Formats

| Format | Description | Use Case |
|--------|-------------|----------|
| `markdown` | Grouped Markdown by source | Notes, blogs, Obsidian |
| `json` | Structured JSON | Programmatic processing, data migration |
| `html` | Standalone HTML with search UI | Browser viewing, sharing |
| `epub` | EPUB e-book | E-readers, iPad |

### Smart Auto-Tagging Rules

BookmarkHub automatically tags bookmarks based on content:

| Keywords | Auto Tag |
|----------|----------|
| python, javascript, rust, golang | `programming` |
| react, vue, css, html | `frontend` |
| ai, llm, gpt, claude, machine learning | `ai` |
| security, hacking, vulnerability, cve | `security` |
| docker, kubernetes, ci/cd | `devops` |
| database, sql, postgres, mongodb | `data` |
| design, ui, ux | `design` |

Manual tags are merged with auto-generated tags (deduplicated).

## 💡 Design Philosophy & Roadmap

### Design Principles

- **Local-first** — Your bookmark data belongs to you, no cloud storage, no third-party auth required
- **Incremental sync** — Only adds new bookmarks, avoids duplicates and data bloat
- **Instant search** — FTS5 full-text index, search as you type
- **Zero barrier** — HackerNews / Lobste.rs work without any authentication

### Roadmap

- [ ] 🐦 Twitter/X bookmark sync (cookie auth)
- [ ] 🔖 Pocket / Instapaper import
- [ ] 📰 RSS feed subscription sync
- [ ] 🤖 LLM-powered smart summaries
- [ ] 🖥️ Web UI dashboard
- [ ] 🔗 Bookmark link health checks
- [ ] 📱 TUI interactive interface (Textual)
- [ ] 🌍 More platforms: ProductHunt, Dev.to, Medium

## 📦 Installation & Deployment

### From Source

```bash
git clone https://github.com/gitstq/bookmarkhub.git
cd bookmarkhub
pip install -e .
```

### Development

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

### Data Storage

- Database: `~/.bookmarkhub/bookmarks.db` (SQLite)
- Exports: `./exports/` directory (default)

## 🤝 Contributing

1. Fork this repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m 'feat: add your feature'`
4. Push branch: `git push origin feature/your-feature`
5. Submit a Pull Request

**Commit convention**: Follow [Angular commit convention](https://github.com/angular/angular/blob/master/CONTRIBUTING.md#commit)

**Bug reports**: Please include OS, Python version, and full error output.

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<a id="繁體中文"></a>

# 🌐 BookmarkHub

**多平台書籤收集、搜尋、分類與匯出 CLI 工具**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-20%20passed-brightgreen.svg)]()

從 HackerNews、Reddit、GitHub Trending、Lobste.rs 一鍵同步書籤到本機，搭配全文搜尋、智慧標籤、多格式匯出，打造你的專屬知識金庫 🏦

## 🎉 專案介紹

每天在 HackerNews、Reddit、GitHub 上看到好內容，隨手收藏然後……再也找不到了？😕

**BookmarkHub** 就是為你打造的命令列書籤管理工具：

- 🔄 **多平台一鍵同步** — 支援 HackerNews、Reddit、GitHub Trending、Lobste.rs
- 🔍 **本機全文搜尋** — 基於 SQLite FTS5，毫秒級檢索，所有資料都在你的本機
- 🏷️ **智慧自動標籤** — 根據內容關鍵字自動分類（程式設計、AI、安全、前端……）
- 📤 **多格式匯出** — Markdown / JSON / HTML（自帶搜尋） / EPUB
- ➕ **手動新增** — 隨時儲存任意網頁連結
- 🎨 **彩色終端機 UI** — Rich 驅動，表格、狀態列、進度提示一應俱全

**差異化亮點**：靈感來源於 [fieldtheory-cli](https://github.com/afar1/fieldtheory-cli)（Twitter 書籤同步工具），但做了全面升級——不限於單一平台，支援 4 大技術社群同步、本機全文檢索、智慧標籤分類、4 種格式匯出，打造完整書籤管理閉環。

## ✨ 核心特性

- 🌐 **多平台同步** — HackerNews / Reddit / GitHub Trending / Lobste.rs 一鍵採集
- 🔍 **FTS5 全文搜尋** — 毫秒級本機檢索，支援標題、描述、標籤跨欄位搜尋
- 🏷️ **智慧自動標籤** — 關鍵字觸發自動分類（programming / ai / security / devops / data / design / frontend）
- 📤 **四格式匯出** — Markdown、JSON、HTML（自帶搜尋 UI）、EPUB（電子書格式）
- 🔄 **增量同步** — 已有書籤自動跳過，只入庫新內容
- 💾 **本機優先** — SQLite 儲存，零雲端依賴，資料完全由你掌控
- 🎨 **彩色終端機** — Rich 驅動的表格、狀態列、彩色輸出
- 📊 **統計面板** — 按來源、標籤維度檢視書籤分佈
- 🪶 **輕量依賴** — 只依賴 click / rich / httpx / beautifulsoup4 四個核心套件

## 🚀 快速開始

### 環境需求

- Python 3.9+
- pip

### 安裝

```bash
git clone https://github.com/gitstq/bookmarkhub.git
cd bookmarkhub
pip install -e .
```

### 基礎使用

```bash
# 同步 HackerNews 熱門
bookmarkhub sync hackernews

# 同步 Reddit（指定子版塊）
bookmarkhub sync reddit --subreddit programming

# 同步 GitHub Trending（按語言）
bookmarkhub sync github --language python --since weekly

# 一鍵同步所有平台
bookmarkhub sync-all

# 手動新增書籤
bookmarkhub add https://example.com -t "Example Site" -T "web,reference"

# 全文搜尋
bookmarkhub search "machine learning"

# 按標籤篩選
bookmarkhub list --tag ai

# 檢視統計
bookmarkhub stats

# 匯出為 Markdown
bookmarkhub export markdown

# 匯出為 HTML（自帶搜尋 UI）
bookmarkhub export html -o my-bookmarks.html

# 匯出為 EPUB 電子書
bookmarkhub export epub -o my-bookmarks.epub
```

## 📖 詳細使用指南

### 同步指令

| 指令 | 說明 | 範例 |
|------|------|------|
| `sync hackernews` | 同步 HN 熱門 | `bookmarkhub sync hackernews -l 50` |
| `sync reddit` | 同步 Reddit | `bookmarkhub sync reddit -s python` |
| `sync github` | 同步 GitHub Trending | `bookmarkhub sync github -L rust --since weekly` |
| `sync lobsters` | 同步 Lobste.rs | `bookmarkhub sync lobsters` |
| `sync-all` | 同步所有平台 | `bookmarkhub sync-all -l 20` |

### 搜尋與篩選

```bash
# 全文搜尋（標題 + 描述 + 標籤）
bookmarkhub search "rust programming"

# 按來源篩選
bookmarkhub search "python" --source hackernews

# 列出所有書籤
bookmarkhub list

# 按來源列出
bookmarkhub list --source reddit

# 按標籤篩選
bookmarkhub list --tag ai
```

### 匯出格式

| 格式 | 說明 | 適用場景 |
|------|------|----------|
| `markdown` | Markdown 文件，按來源分組 | 筆記、部落格、Obsidian |
| `json` | 結構化 JSON | 程式化處理、資料遷移 |
| `html` | 自帶搜尋 UI 的獨立 HTML 頁面 | 瀏覽器檢視、分享 |
| `epub` | EPUB 電子書 | 電子閱讀器、iPad |

### 智慧自動標籤規則

BookmarkHub 會根據書籤內容自動打標籤：

| 關鍵字 | 自動標籤 |
|--------|----------|
| python, javascript, rust, golang | `programming` |
| react, vue, css, html | `frontend` |
| ai, llm, gpt, claude, machine learning | `ai` |
| security, hacking, vulnerability, cve | `security` |
| docker, kubernetes, ci/cd | `devops` |
| database, sql, postgres, mongodb | `data` |
| design, ui, ux | `design` |

你也可以手動新增標籤，手動標籤和自動標籤會合併去重。

## 💡 設計思路與迭代規劃

### 設計理念

- **本機優先** — 你的書籤資料屬於你，不儲存在雲端，不依賴第三方認證
- **增量同步** — 只新增新書籤，不重複入庫，避免資料膨脹
- **即搜即得** — FTS5 全文索引，輸入即搜尋，無需等待
- **零門檻上手** — HackerNews / Lobste.rs 無需認證即可同步

### 後續迭代計畫

- [ ] 🐦 Twitter/X 書籤同步（Cookie 認證）
- [ ] 🔖 Pocket / Instapaper 匯入
- [ ] 📰 RSS 源訂閱同步
- [ ] 🤖 LLM 驅動的智慧摘要生成
- [ ] 🖥️ Web UI 儀表板
- [ ] 🔗 書籤連結健康檢查
- [ ] 📱 TUI 互動介面（Textual）
- [ ] 🌍 更多平台：ProductHunt、Dev.to、Medium

## 📦 安裝與部署

### 從原始碼安裝

```bash
git clone https://github.com/gitstq/bookmarkhub.git
cd bookmarkhub
pip install -e .
```

### 開發環境

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

## 🤝 貢獻指南

1. Fork 本儲存庫
2. 建立特性分支：`git checkout -b feature/your-feature`
3. 提交變更：`git commit -m 'feat: add your feature'`
4. 推送分支：`git push origin feature/your-feature`
5. 提交 Pull Request

## 📄 開源協議

本專案基於 [MIT 協議](LICENSE) 開源，可自由使用、修改和分發。

---

<a id="日本語"></a>

# 🌐 BookmarkHub

**マルチプラットフォームのブックマーク収集・検索・整理・エクスポート CLI ツール**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-20%20passed-brightgreen.svg)]()

HackerNews、Reddit、GitHub Trending、Lobste.rs からワンクリックでブックマークを同期。全文検索、スマートタグ付け、マルチフォーマットエクスポートで、あなただけの知識バンクを構築 🏦

## 🎉 紹介

HackerNews、Reddit、GitHub で毎日素晴らしいコンテンツを見つけてブックマークしても……後で見つけられない？😕

**BookmarkHub** はそんなあなたのための CLI ブックマークマネージャーです：

- 🔄 **マルチプラットフォーム一括同期** — HackerNews、Reddit、GitHub Trending、Lobste.rs
- 🔍 **ローカル全文検索** — SQLite FTS5 でミリ秒検索、データはすべてローカルに
- 🏷️ **スマート自動タグ付け** — キーワードに基づく自動分類
- 📤 **マルチフォーマットエクスポート** — Markdown / JSON / HTML（検索 UI 付き） / EPUB
- ➕ **手動追加** — 任意の URL をいつでも保存
- 🎨 **リッチターミナル UI** — Rich によるテーブル、スピナー、カラフルな出力

**差別化のポイント**：[fieldtheory-cli](https://github.com/afar1/fieldtheory-cli)（Twitter ブックマーク同期ツール）にインスパイアされましたが、全面的にアップグレード — 単一プラットフォームに限定せず、4つの主要テックコミュニティに対応、ローカル全文検索、スマートタグ付け、4形式エクスポートで完全なブックマーク管理ワークフローを実現。

## ✨ 主な機能

- 🌐 **マルチプラットフォーム同期** — HackerNews / Reddit / GitHub Trending / Lobste.rs
- 🔍 **FTS5 全文検索** — タイトル、説明、タグのミリ秒ローカル検索
- 🏷️ **スマート自動タグ付け** — キーワードトリガーによる分類
- 📤 **4形式エクスポート** — Markdown、JSON、HTML（検索 UI 付き）、EPUB
- 🔄 **増分同期** — 既存のブックマークをスキップ、新規コンテンツのみ追加
- 💾 **ローカルファースト** — SQLite ストレージ、クラウド依存なし
- 🎨 **カラフルターミナル** — Rich によるテーブル、スピナー、カラー出力
- 📊 **統計ダッシュボード** — ソースとタグによる分布表示
- 🪶 **軽量** — コア依存は4つだけ：click / rich / httpx / beautifulsoup4

## 🚀 クイックスタート

### 必要環境

- Python 3.9+
- pip

### インストール

```bash
git clone https://github.com/gitstq/bookmarkhub.git
cd bookmarkhub
pip install -e .
```

### 基本的な使い方

```bash
# HackerNews から同期
bookmarkhub sync hackernews

# Reddit から同期（サブレディット指定）
bookmarkhub sync reddit --subreddit programming

# GitHub Trending から同期（言語指定）
bookmarkhub sync github --language python --since weekly

# 全プラットフォームを一括同期
bookmarkhub sync-all

# ブックマークを手動追加
bookmarkhub add https://example.com -t "Example Site" -T "web,reference"

# 全文検索
bookmarkhub search "machine learning"

# タグで絞り込み
bookmarkhub list --tag ai

# 統計を表示
bookmarkhub stats

# Markdown でエクスポート
bookmarkhub export markdown

# HTML でエクスポート（検索 UI 付き）
bookmarkhub export html -o my-bookmarks.html

# EPUB 電子書籍でエクスポート
bookmarkhub export epub -o my-bookmarks.epub
```

## 💡 設計思想とロードマップ

### 設計原則

- **ローカルファースト** — データはあなたのもの、クラウド保存なし、サードパーティ認証不要
- **増分同期** — 新しいブックマークのみ追加、重複を回避
- **即座に検索** — FTS5 フルテキストインデックス、入力と同時に検索
- **ゼロ障壁** — HackerNews / Lobste.rs は認証なしで利用可能

### ロードマップ

- [ ] 🐦 Twitter/X ブックマーク同期（Cookie 認証）
- [ ] 🔖 Pocket / Instapaper インポート
- [ ] 📰 RSS フィード購読同期
- [ ] 🤖 LLM 駆動のスマート要約
- [ ] 🖥️ Web UI ダッシュボード
- [ ] 🔗 ブックマークリンク健全性チェック
- [ ] 📱 TUI インタラクティブインターフェース（Textual）
- [ ] 🌍 追加プラットフォーム：ProductHunt、Dev.to、Medium

## 🤝 コントリビュート

1. このリポジトリをフォーク
2. フィーチャーブランチを作成：`git checkout -b feature/your-feature`
3. 変更をコミット：`git commit -m 'feat: add your feature'`
4. ブランチをプッシュ：`git push origin feature/your-feature`
5. Pull Request を提出

## 📄 ライセンス

このプロジェクトは [MIT ライセンス](LICENSE) のもとで公開されています。
