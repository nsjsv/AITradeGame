# AI Agent 项目规范

## Coding 八荣八耻

- 以瞎猜接口为耻，以认真查询为荣
- 以模糊执行为耻，以寻求确认为荣
- 以臆想业务为耻，以人类确认为荣
- 以创造接口为耻，以复用现有为荣
- 以跳过验证为耻，以主动测试为荣
- 以破坏架构为耻，以遵循规范为荣
- 以假装理解为耻，以诚实无知为荣
- 以盲目修改为耻，以谨慎重构为荣

## 项目结构

**注意：** 项目已完成前端迁移，旧的 `static/` 和 `templates/` 目录已被移除。现在使用现代化的 Next.js 15 + React 19 前端架构。

```
project/
├── main.py                # 后端启动入口
├── requirements.txt       # Python 依赖
├── backend/
│   ├── core/              # 核心交易逻辑（引擎、策略、AI）
│   ├── data/              # 数据层（数据库、市场数据、缓存）
│   ├── api/               # API 路由和控制器
│   ├── models/            # 数据模型（ORM）
│   ├── services/          # 业务服务（通知、监控）
│   ├── utils/             # 工具函数
│   ├── config/            # 后端配置
│   └── tests/             # 后端测试
├── frontend/              # 现代化前端（Next.js 15 + React 19）
│   ├── app/               # Next.js App Router
│   │   ├── (routes)/      # 路由组
│   │   ├── api/           # API Routes
│   │   ├── layout.tsx     # 根布局
│   │   └── page.tsx       # 首页
│   ├── components/        # React 组件
│   │   ├── ui/            # Shadcn UI 组件
│   │   └── features/      # 业务组件
│   ├── lib/               # 工具库
│   │   ├── api.ts         # API 调用封装
│   │   ├── utils.ts       # 工具函数
│   │   └── types.ts       # TypeScript 类型
│   ├── hooks/             # 自定义 Hooks
│   ├── store/             # 状态管理（Zustand/Jotai）
│   ├── public/            # 静态资源
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   └── next.config.js
├── scripts/               # 部署和运维脚本
└── docker-compose.yml     # 容器编排
```

## 命名规范

### 后端（Python）
- **文件名**: `snake_case.py`
- **类名**: `PascalCase`
- **函数/变量**: `snake_case`
- **常量**: `UPPER_SNAKE_CASE`
- **私有成员**: `_leading_underscore`

### 前端（TypeScript/React）
- **文件名**: `PascalCase.tsx` (组件) / `kebab-case.ts` (工具)
- **组件名**: `PascalCase`
- **函数/变量**: `camelCase`
- **常量**: `UPPER_SNAKE_CASE`
- **类型/接口**: `PascalCase`
- **私有成员**: `_leadingUnderscore` 或 `#private`

## 代码组织

### 代码质量原则
- **保持文件精简**：一个文件专注一个职责
- **函数简短**：单个函数不超过 50 行（复杂逻辑除外）
- **类职责单一**：一个类只做一件事
- **避免深层嵌套**：最多 3 层缩进
- **文件行数建议**：
  - 工具函数文件：< 200 行
  - 单个类文件：< 300 行
  - 复杂模块：< 500 行
  - 配置/路由文件：< 400 行
  - 超过 500 行时考虑拆分

### 后端模块职责
- `core/` - 交易引擎、AI 决策、策略执行
- `data/` - 数据库操作、市场数据获取、缓存
- `api/` - RESTful API、WebSocket 接口
- `models/` - SQLAlchemy 模型、数据结构
- `services/` - 独立业务逻辑（通知、日志、监控）
- `utils/` - 纯函数工具（时间、格式化、验证）

### 前端模块职责
- `app/` - Next.js 页面和路由（App Router）
- `components/ui/` - Shadcn UI 基础组件
- `components/features/` - 业务组件（交易面板、图表、表格）
- `lib/` - 工具库（API 封装、工具函数、类型定义）
- `hooks/` - 自定义 React Hooks
- `store/` - 全局状态管理（Zustand/Jotai）

### 后端文件结构
```python
"""模块文档字符串 - 说明模块用途"""

# 1. 标准库导入
import os
from datetime import datetime

# 2. 第三方库导入
import pandas as pd
from flask import Flask

# 3. 本地导入
from backend.core import Engine
from backend.utils import format_price

# 4. 常量定义
MAX_POSITION = 100

# 5. 类和函数定义
class Trader:
    """类文档字符串"""
    pass
```

### 前端文件结构
```typescript
// 1. React 导入
'use client' // 客户端组件标记（需要时）
import { useState, useEffect } from 'react'

// 2. 第三方库导入
import { Card } from '@/components/ui/card'
import { LineChart } from 'lucide-react'

// 3. 本地导入
import { formatPrice } from '@/lib/utils'
import { api } from '@/lib/api'
import type { Trade } from '@/lib/types'

// 4. 常量定义
const MAX_POSITION = 100

// 5. 组件定义
export function TradePanel() {
  const [trades, setTrades] = useState<Trade[]>([])
  
  return (
    <Card>
      {/* ... */}
    </Card>
  )
}
```

## 依赖管理

### 后端
- 使用 `requirements.txt` 或 `pyproject.toml`
- 核心依赖和开发依赖分离
- 固定版本号避免兼容性问题

### 前端
- 使用 `package.json` 管理依赖
- 锁定版本使用 `pnpm-lock.yaml`（推荐 pnpm）
- 区分 dependencies 和 devDependencies
- 核心技术栈：
  - Next.js 15 - React 框架
  - React 19 - UI 库
  - TypeScript - 类型安全
  - Tailwind CSS 4 - 样式框架
  - Shadcn UI - 组件库
  - Lucide Icons - 图标库

## 配置管理

### 后端
- 配置文件放在 `backend/config/`
- 敏感信息使用环境变量
- 提供 `.env.example` 模板
- 不同环境使用不同配置文件

### 前端
- 环境变量使用 `.env.local` 和 `.env.production`
- 公开变量前缀：`NEXT_PUBLIC_`
- API 地址等配置通过环境变量注入
- 构建时配置在 `next.config.js`

## 错误处理

```python
# 明确的异常类型
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"操作失败: {e}")
    raise
```

## 日志规范

```python
import logging

logger = logging.getLogger(__name__)

# 使用合适的日志级别
logger.debug("调试信息")
logger.info("正常流程")
logger.warning("警告信息")
logger.error("错误信息")
logger.critical("严重错误")
```

## 数据库

- 使用 SQLAlchemy ORM
- 模型定义在 `models/`
- 数据库操作封装在 `data/`
- 使用迁移工具管理 schema 变更

## API 设计

### 后端 API
- RESTful 风格
- 统一响应格式：`{"success": bool, "data": any, "error": str}`
- 使用 HTTP 状态码
- WebSocket 用于实时数据推送
- CORS 配置允许前端跨域

### 前端 API 调用
- 使用 fetch 或 axios 封装在 `lib/api.ts`
- 请求拦截器添加 token
- 响应拦截器处理错误
- TypeScript 类型定义在 `lib/types.ts`
- 使用 React Query/SWR 管理服务端状态

## 测试

### 后端
- 单元测试覆盖核心逻辑
- 测试文件命名：`test_*.py`
- 使用 pytest
- Mock 外部依赖

### 前端
- 组件测试使用 Jest + React Testing Library
- E2E 测试使用 Playwright
- 测试文件命名：`*.test.tsx` 或 `*.spec.tsx`
- Mock API 调用

## 文档

- 复杂逻辑必须注释
- 公共 API 必须有文档字符串
- README.md 包含：项目介绍、安装、使用、配置
- 关键决策记录在 docs/

## Git 规范

- 提交信息格式：`<type>: <description>`
- type: feat, fix, refactor, docs, test, chore
- 小步提交，单一职责
- 敏感信息不入库

## 性能考虑

- 数据库查询使用索引
- 缓存频繁访问的数据
- 异步处理耗时操作
- 避免循环中的重复计算

## 安全

- 输入验证
- SQL 注入防护（使用 ORM）
- API 密钥不硬编码
- 敏感数据加密存储

## 前后端通信

- 后端提供 RESTful API 和 WebSocket
- 前端通过 fetch/axios 请求获取数据
- 实时数据通过 WebSocket 推送
- 后端默认端口：5000
- 前端开发服务器端口：3000
- 生产环境前端构建后独立部署或 Nginx 代理

## 前端样式规范

- 使用 Tailwind CSS 工具类
- 组件样式优先使用 Shadcn UI
- 自定义样式使用 `cn()` 工具函数合并类名
- 响应式设计：`sm:` `md:` `lg:` `xl:` `2xl:`
- 暗色模式支持：`dark:` 前缀
- 图标统一使用 Lucide Icons

## 部署

### 开发环境
- 后端：`python main.py`
- 前端：`cd frontend && pnpm dev`

### 生产环境
- 后端：使用 gunicorn 或 uvicorn
- 前端：`pnpm build` 后部署（Vercel/自托管）
- 使用 Nginx 反向代理
- 或使用 Docker Compose 一键部署

## AI 维护提示

### 重构优先级
1. 保持功能不变
2. 前后端代码完全分离
3. 按模块职责移动文件
4. 更新导入路径
5. 运行测试验证

### 验证清单
- 后端：导入是否正常、API 是否可访问
- 前端：组件是否正常渲染、API 调用是否成功
- 测试是否通过
- 配置是否正确

### 重要规则
- **除非用户明确要求，否则不要创建任何文档文件**
- 不要创建 README.md、CHANGELOG.md、TODO.md 等文档
- 不要创建设计文档、架构文档、API 文档
- 代码注释和文档字符串除外
- 专注于编写可运行的代码

### 代码质量检查
- 文件超过 500 行时主动提示拆分
- 函数超过 50 行时考虑重构
- 类超过 300 行时考虑拆分
- 发现重复代码时主动提取
- 保持代码清晰易懂优先于简洁
