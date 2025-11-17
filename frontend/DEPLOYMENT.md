# 前端部署指南

## 开发环境

### 前置要求
- Node.js 20+ 
- npm 或 pnpm

### 启动步骤

1. **安装依赖**
```bash
cd frontend
npm install
# 或使用 pnpm
pnpm install
```

2. **配置环境变量**
```bash
# 复制环境变量示例文件
cp .env.example .env.local

# 编辑 .env.local，确保 API 地址正确
# NEXT_PUBLIC_API_BASE_URL=http://localhost:5000
# NEXT_PUBLIC_WS_URL=ws://localhost:5000
```

3. **启动开发服务器**
```bash
npm run dev
```

开发服务器将在 `http://localhost:3000` 启动

4. **验证连接**
- 前端: http://localhost:3000
- 后端 API: http://localhost:5000
- 确保后端服务已启动（在项目根目录运行 `python main.py`）

## 生产环境

### 构建步骤

1. **配置生产环境变量**
```bash
# 复制生产环境配置示例
cp .env.production.example .env.production

# 编辑 .env.production，设置生产环境 API 地址
# NEXT_PUBLIC_API_BASE_URL=https://api.your-domain.com
# NEXT_PUBLIC_WS_URL=wss://api.your-domain.com
# NEXT_PUBLIC_ENV=production
```

2. **构建生产版本**
```bash
npm run build
```

3. **启动生产服务器**
```bash
npm run start
```

生产服务器将在 `http://localhost:3000` 启动

### 部署选项

#### 选项 1: Vercel（推荐）
1. 将代码推送到 Git 仓库
2. 在 Vercel 导入项目
3. 配置环境变量（在 Vercel 项目设置中）
4. 自动部署

#### 选项 2: 自托管（Docker）
```bash
# 构建 Docker 镜像
docker build -t aitradegame-frontend .

# 运行容器
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_BASE_URL=https://api.your-domain.com \
  -e NEXT_PUBLIC_WS_URL=wss://api.your-domain.com \
  aitradegame-frontend
```

#### 选项 3: Nginx 反向代理
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## 环境变量说明

| 变量名 | 说明 | 开发环境 | 生产环境 |
|--------|------|----------|----------|
| `NEXT_PUBLIC_API_BASE_URL` | 后端 API 地址 | `http://localhost:5000` | `https://api.your-domain.com` |
| `NEXT_PUBLIC_WS_URL` | WebSocket 地址 | `ws://localhost:5000` | `wss://api.your-domain.com` |
| `NEXT_PUBLIC_ENV` | 环境标识 | `development` | `production` |

## 故障排查

### 前端无法连接后端
1. 检查后端是否运行在端口 5000
2. 检查 `.env.local` 中的 API 地址是否正确
3. 检查浏览器控制台的网络请求错误

### 构建失败
1. 清除缓存: `rm -rf .next`
2. 重新安装依赖: `rm -rf node_modules && npm install`
3. 检查 TypeScript 错误: `npm run lint`

### 端口冲突
如果端口 3000 被占用，可以指定其他端口:
```bash
PORT=3001 npm run dev
```

## 性能优化

### 生产环境优化
- ✅ 启用 React Compiler
- ✅ 启用 gzip 压缩
- ✅ 图片格式优化（AVIF/WebP）
- ✅ 移除 X-Powered-By 头部
- ✅ React 严格模式

### 进一步优化建议
- 使用 CDN 加速静态资源
- 启用 HTTP/2
- 配置缓存策略
- 使用 Service Worker（PWA）
