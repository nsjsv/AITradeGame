import type { NextConfig } from "next";
import { config as loadEnv } from "dotenv";
import { existsSync } from "fs";
import { join } from "path";

const repoRoot = join(process.cwd(), "..");
const envFiles = [
  ".env.local",
  process.env.NODE_ENV === "production" ? ".env.production" : ".env.development",
  ".env",
].filter(Boolean) as string[];

envFiles.forEach((file) => {
  const filePath = join(repoRoot, file);
  if (existsSync(filePath)) {
    loadEnv({ path: filePath, override: true });
  }
});

const nextConfig: NextConfig = {
  /* config options here */
  reactCompiler: true,
  
  // ============================================================================
  // 环境变量配置
  // ============================================================================
  env: {
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL,
    NEXT_PUBLIC_BROWSER_API_BASE_URL: process.env.NEXT_PUBLIC_BROWSER_API_BASE_URL,
    NEXT_PUBLIC_WS_URL: process.env.NEXT_PUBLIC_WS_URL,
    NEXT_PUBLIC_ENV: process.env.NEXT_PUBLIC_ENV,
  },
  
  // ============================================================================
  // 生产构建优化
  // ============================================================================
  
  // 移除 X-Powered-By 头部（安全性）
  poweredByHeader: false,
  
  // 启用 gzip 压缩
  compress: true,
  
  // 严格模式（React 18+）
  reactStrictMode: true,
  
  // ============================================================================
  // 图片优化配置
  // ============================================================================
  images: {
    // 支持的图片格式（按优先级）
    formats: ['image/avif', 'image/webp'],
    
    // 图片域名白名单（如果需要加载外部图片）
    // remotePatterns: [
    //   {
    //     protocol: 'https',
    //     hostname: 'example.com',
    //   },
    // ],
  },
  
  // ============================================================================
  // 输出配置
  // ============================================================================
  
  // 输出模式
  // - 'standalone': 生成独立的服务器包（推荐用于 Docker）
  // - undefined: 默认模式
  // output: 'standalone',
  
  // ============================================================================
  // 开发体验优化
  // ============================================================================
  
  // TypeScript 类型检查（构建时）
  typescript: {
    // 生产构建时忽略类型错误（不推荐，仅用于紧急情况）
    // ignoreBuildErrors: false,
  },
};

export default nextConfig;
