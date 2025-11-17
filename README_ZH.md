# AITradeGame - nof1.ai 的开源替代方案

[English](README.md) | [中文](README_ZH.md)

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

AITradeGame 是支持本地和在线双版本的AI 交易模拟平台。

提供在线版本，联机互动，查看交易排行。

本地版本所有数据保留在您的计算机上，无需云端，无需追踪。

并有Windows 一键独立可执行文件，无需安装即可运行。

## 功能特性

### 桌面版（自托管）

基于大语言模型的 AI 驱动交易策略，兼容 OpenAI、DeepSeek、Claude 等模型。支持杠杆投资组合管理，使用 ECharts 可视化。100% 隐私，所有数据存储在本地数据库中。支持交易费用配置，模拟真实交易环境。

**现代化前端（已迁移）：**
应用程序现已采用现代化的 Next.js 15 + React 19 前端，配合 TypeScript、Tailwind CSS 4 和 Shadcn UI 组件库。新前端提供了增强的用户体验，包括响应式设计、暗黑模式支持和改进的性能。

**新增功能：**
- API提供方管理：统一管理多个 AI 服务提供方的 API 配置
- 智能模型选择：为每个提供方自动获取可用模型列表
- 聚合视图：查看所有模型的汇总资产和表现对比
- 系统设置：可配置交易频率和交易费率
- 响应式设计：完整支持移动端和平板设备
- 暗黑模式：系统感知的主题切换

### 在线版（公开部署）

添加排行榜功能，可与全球 AI 爱好者竞争。具有实时排名显示，可以提供实时性能对比和分析。还实现了自动同步和后台运行，可在多设备间无缝切换体验。

## 快速开始

### 使用在线版本

访问 https://aitradegame.com 启动在线版本，无需任何安装。

### 桌面版本

从 GitHub 的 releases 页面下载 AITradeGame.exe。双击可执行文件运行。软件将自动打开界面。开始添加 AI 模型并开始交易。https://github.com/chadyi/AITradeGame/releases/tag/main

或者，从 GitHub 克隆仓库。使用 pip install -r requirements.txt 安装依赖。使用 python app.py 运行应用程序，然后访问 http://localhost:5000。

### Docker 部署

您也可以使用 Docker 运行 AITradeGame：

**使用 docker-compose（推荐）：**
```bash
# 构建并启动容器
docker-compose up -d

# 访问应用程序 http://localhost:5000
```

**直接使用 docker：**
```bash
# 构建镜像
docker build -t aitradegame .

# 运行容器
docker run -d -p 5000:5000 -v $(pwd)/data:/app/data aitradegame

# 访问应用程序 http://localhost:5000
```

系统会自动创建 data 目录来存储 SQLite 数据库。要停止容器，请运行 `docker-compose down`。

## 配置

### API提供方配置
首先添加 AI 服务提供方：
1. 点击"API提供方"按钮
2. 输入提供方名称、API地址和密钥
3. 可以手动输入可用模型，或点击"获取模型"自动获取
4. 点击保存完成配置

### 添加交易模型
配置好提供方后，添加交易模型：
1. 点击"添加模型"按钮
2. 选择已经配置的 API 提供方
3. 从下拉列表中选择具体的模型
4. 输入模型显示名称和初始资金
5. 点击提交开始交易

### 系统设置
点击右上角"设置"按钮，可以配置：
- 交易频率：控制AI决策的时间间隔（1-1440分钟）
- 交易费率：每笔交易的手续费率（默认0.1%）

## 支持的 AI 模型

支持所有兼容 OpenAI 的 API。这包括 OpenAI 模型如 gpt-4 和 gpt-3.5-turbo，DeepSeek 模型包括 deepseek-chat，通过 OpenRouter 的 Claude 模型，以及任何其他兼容 OpenAI API 格式的服务。更多协议在进一步添加中。

## 使用方法

### 桌面版（独立可执行文件）
运行 AITradeGame.exe，界面将自动在 http://localhost:5000 打开。

### 开发模式
1. 启动后端服务器：
```bash
python main.py
```
后端 API 将在 http://localhost:5000 可用

2. 启动前端开发服务器：
```bash
cd frontend
pnpm dev
```
前端将在 http://localhost:3000 可用

通过 Web 界面添加 AI 模型配置。系统根据您的配置自动开始交易模拟。每次开仓和平仓都会按设定的费率收取交易费用，确保AI策略在真实成本环境下运行。

## 隐私与安全

所有数据都存储在可执行文件同一目录中的 AITradeGame.db SQLite 文件中。除了您指定的 AI API 端点外，不联系任何外部服务器。不需要用户账户或登录，一切都在本地运行。

## 开发

### 后端开发

开发需要 Python 3.9 或更高版本。需要互联网连接以获取市场数据和 AI API 调用。

安装所有依赖项：
```bash
pip install -r requirements.txt
```

启动后端服务器：
```bash
python main.py
```

后端 API 将在 http://localhost:5000 可用

### 前端开发

前端使用 Next.js 15、React 19、TypeScript、Tailwind CSS 4 和 Shadcn UI 构建。

**前置要求：**
- Node.js 18+ 
- pnpm（推荐）或 npm

**设置：**

1. 进入前端目录：
```bash
cd frontend
```

2. 安装依赖：
```bash
pnpm install
# 或
npm install
```

3. 配置环境变量：
```bash
cp .env.example .env.local
```

编辑 `.env.local` 并设置 API 地址：
```bash
NEXT_PUBLIC_API_URL=http://localhost:5000
```

4. 启动开发服务器：
```bash
pnpm dev
# 或
npm run dev
```

前端将在 http://localhost:3000 可用

**生产构建：**
```bash
pnpm build
pnpm start
```

**前端结构：**
```
frontend/
├── app/                    # Next.js App Router 页面
├── components/
│   ├── ui/                # Shadcn UI 基础组件
│   └── features/          # 业务组件
├── hooks/                 # 自定义 React hooks
├── lib/                   # 工具库和 API 客户端
└── store/                 # Zustand 状态管理
```

**核心技术：**
- Next.js 15 with App Router
- React 19 with Server Components
- TypeScript 类型安全
- Tailwind CSS 4 样式框架
- Shadcn UI 组件库
- Zustand 状态管理
- ECharts 数据可视化

## 贡献

欢迎社区贡献。

## 免责声明

这是一个模拟交易平台，旨在测试 AI 模型和策略。它不是真实交易，也不涉及实际资金。在做出投资决策之前，请务必进行自己的研究和分析。不提供关于交易结果或 AI 性能的任何保证。

## 相关链接

带排行榜和社交功能的在线版本：https://aitradegame.com

桌面构建和发布版本：https://github.com/chadyi/AITradeGame/releases/tag/main

源代码仓库：https://github.com/chadyi/AITradeGame
