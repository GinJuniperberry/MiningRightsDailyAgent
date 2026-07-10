# 前端多阶段构建：Node 构建 + Nginx 服务

# ===== Stage 1: 构建 React 应用 =====
FROM node:20-alpine AS builder

WORKDIR /app

# 先复制 package 文件，利用 Docker 缓存层
COPY package.json package-lock.json* ./
RUN npm ci --no-audit --no-fund

# 复制源代码并构建
COPY . .
RUN npm run build

# ===== Stage 2: Nginx 静态服务 =====
FROM nginx:alpine

# 复制自定义 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 确保权限正确
RUN chmod -R 755 /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
