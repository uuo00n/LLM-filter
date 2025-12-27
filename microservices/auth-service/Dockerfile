FROM golang:1.24-alpine

WORKDIR /app

# 设置 Go 代理
ENV GOPROXY=https://goproxy.cn,direct

# 预下载依赖，利用 Docker 缓存层
COPY go.mod go.sum ./
RUN go mod download

# 复制源代码
COPY . .

# 整理依赖（确保新加的 swaggo 依赖被正确拉取）
RUN go mod tidy

# 编译
RUN go build -o auth-service .

# 运行时暴露端口
EXPOSE 8081

# 启动服务
CMD ["./auth-service"]
