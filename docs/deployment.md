# 部署指南

本文档提供 FivJourney Tools 旅游全程追踪系统的部署指南，包括本地开发环境、Docker部署和生产环境部署。

## 👨‍💻 作者

**Charlie ZHANG**  
📧 Email: sunnypig2002@gmail.com

## 🚀 部署选项

### 1. 本地开发部署

适合开发和测试环境。

#### 环境要求

- Python 3.10+
- uv包管理器
- SQLite（默认）或PostgreSQL

#### 部署步骤

```bash
# 1. 克隆项目
git clone <repository-url>
cd fivjourney-tools

# 2. 安装uv（如果尚未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
# 或
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows

# 3. 创建虚拟环境并安装依赖
uv sync

# 4. 配置环境变量
cp config.env .env
# 编辑.env文件配置数据库等设置

# 5. 初始化数据库
uv run python -c "
from app.core.database import engine
from app.models import Base
import asyncio

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(init_db())
"

# 6. 启动应用
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 使用Makefile简化部署

```bash
# 安装依赖
make install

# 启动开发服务器
make dev

# 运行测试
make test

# 代码格式化
make format
```

### 2. Docker部署

适合快速部署和容器化环境。

#### 单容器部署

```bash
# 构建镜像
docker build -t fivjourney-tools .

# 运行容器
docker run -d \
  --name fivjourney-tools-app \
  -p 8000:8000 \
  -e DATABASE_URL="sqlite+aiosqlite:///./travel_tracker.db" \
  -e SECRET_KEY="your-secret-key" \
  fivjourney-tools
```

#### Docker Compose部署

使用`docker-compose.yml`进行多容器部署：

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重建镜像
docker-compose up --build -d
```

默认配置包含：
- 应用服务（端口8000）
- PostgreSQL数据库（端口5432）
- 数据卷持久化

#### Docker环境变量

在`.env`文件中配置：

```bash
# 应用配置
SECRET_KEY=your-super-secret-key-here
DEBUG=false
API_V1_STR=/api/v1

# 数据库配置
POSTGRES_DB=travel_tracker
POSTGRES_USER=travel_user
POSTGRES_PASSWORD=travel_password
DATABASE_URL=postgresql+asyncpg://travel_user:travel_password@db:5432/travel_tracker

# 可选配置
CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. 生产环境部署

适合生产环境的高可用部署。

#### 架构概述

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Nginx     │───▶│  FastAPI    │───▶│ PostgreSQL  │
│ (反向代理)   │    │   应用服务   │    │   数据库     │
└─────────────┘    └─────────────┘    └─────────────┘
        │                  │
        ▼                  ▼
┌─────────────┐    ┌─────────────┐
│   SSL证书    │    │   Redis     │
│  (Let's E.)  │    │   (缓存)     │
└─────────────┘    └─────────────┘
```

#### 方案1：传统服务器部署

**1. 系统要求**

- Ubuntu 20.04+ 或 CentOS 8+
- 2GB+ RAM
- 20GB+ 存储空间
- Python 3.10+
- PostgreSQL 13+
- Nginx
- Redis（可选）

**2. 安装依赖**

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3.10 python3.10-venv python3-pip postgresql postgresql-contrib nginx redis-server

# CentOS/RHEL
sudo dnf install -y python3.10 python3.10-venv python3-pip postgresql postgresql-server postgresql-contrib nginx redis
```

**3. 数据库配置**

```bash
# 启动PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 创建数据库和用户
sudo -u postgres psql << EOF
CREATE DATABASE travel_tracker;
CREATE USER travel_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE travel_tracker TO travel_user;
\q
EOF
```

**4. 应用部署**

```bash
# 创建应用用户
sudo useradd -m -s /bin/bash travel-app
sudo su - travel-app

# 部署应用
git clone <repository-url> /home/travel-app/app
cd /home/travel-app/app

# 安装uv和依赖
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
uv sync --extra prod

# 配置环境变量
cp config.env .env
# 编辑.env文件设置生产配置

# 数据库迁移
uv run alembic upgrade head
```

**5. Systemd服务配置**

创建`/etc/systemd/system/fivjourney-tools.service`：

```ini
[Unit]
Description=Travel Tracker FastAPI Application
After=network.target

[Service]
Type=exec
User=travel-app
Group=travel-app
WorkingDirectory=/home/travel-app/app
Environment=PATH=/home/travel-app/.cargo/bin:/home/travel-app/app/.venv/bin
ExecStart=/home/travel-app/.cargo/bin/uv run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
ExecReload=/bin/kill -HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable fivjourney-tools
sudo systemctl start fivjourney-tools
sudo systemctl status fivjourney-tools
```

**6. Nginx配置**

创建`/etc/nginx/sites-available/fivjourney-tools`：

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # 重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL配置
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    
    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # 客户端最大请求大小
    client_max_body_size 50M;
    
    # 代理设置
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }
    
    # 静态文件缓存
    location /static {
        alias /home/travel-app/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # API文档缓存
    location /docs {
        proxy_pass http://127.0.0.1:8000;
        expires 1h;
        add_header Cache-Control "public";
    }
}
```

启用站点：

```bash
sudo ln -s /etc/nginx/sites-available/fivjourney-tools /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

**7. SSL证书配置**

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 设置自动续期
sudo crontab -e
# 添加以下行：
# 0 12 * * * /usr/bin/certbot renew --quiet
```

#### 方案2：云平台部署

**AWS部署示例**

1. **ECS Fargate部署**

```yaml
# task-definition.json
{
  "family": "fivjourney-tools",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "fivjourney-tools",
      "image": "your-account.dkr.ecr.region.amazonaws.com/fivjourney-tools:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql+asyncpg://user:pass@rds-endpoint:5432/db"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/fivjourney-tools",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

2. **RDS数据库配置**

```bash
# 创建RDS PostgreSQL实例
aws rds create-db-instance \
    --db-instance-identifier fivjourney-tools-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --master-username postgres \
    --master-user-password securepassword \
    --allocated-storage 20 \
    --vpc-security-group-ids sg-12345678 \
    --db-subnet-group-name default
```

**Google Cloud Run部署**

```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/fivjourney-tools', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/fivjourney-tools']
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'fivjourney-tools'
      - '--image'
      - 'gcr.io/$PROJECT_ID/fivjourney-tools'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
```

## 📊 监控和维护

### 应用监控

**1. 健康检查**

```python
# 在main.py中添加
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}
```

**2. 日志配置**

```python
# app/core/logging.py
import logging
from logging.handlers import RotatingFileHandler

# 配置日志轮转
handler = RotatingFileHandler(
    'logs/app.log', 
    maxBytes=10485760,  # 10MB
    backupCount=5
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[handler]
)
```

**3. Prometheus监控**

```python
# 添加到requirements
prometheus-fastapi-instrumentator

# 在main.py中
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)
```

### 数据库维护

**1. 定期备份**

```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/backups"
DB_NAME="travel_tracker"
DATE=$(date +%Y%m%d_%H%M%S)

pg_dump -h localhost -U travel_user $DB_NAME | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# 清理7天前的备份
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete
```

**2. 数据库迁移**

```bash
# 生产环境迁移
uv run alembic upgrade head

# 备份后迁移
pg_dump travel_tracker > backup_before_migration.sql
uv run alembic upgrade head
```

### 性能优化

**1. 连接池配置**

```python
# app/core/database.py
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

**2. 缓存配置**

```python
# 使用Redis缓存
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fivjourney-tools")
```

## 🔧 故障排除

### 常见问题

**1. 数据库连接失败**

```bash
# 检查数据库状态
sudo systemctl status postgresql

# 检查连接
psql -h localhost -U travel_user -d travel_tracker

# 查看日志
sudo journalctl -u postgresql -f
```

**2. 应用启动失败**

```bash
# 检查应用状态
sudo systemctl status fivjourney-tools

# 查看错误日志
sudo journalctl -u fivjourney-tools -f

# 手动启动测试
cd /home/travel-app/app
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

**3. Nginx配置问题**

```bash
# 测试配置
sudo nginx -t

# 重新加载
sudo systemctl reload nginx

# 查看错误日志
sudo tail -f /var/log/nginx/error.log
```

### 安全检查清单

- [ ] 数据库密码强度充足
- [ ] SSL证书正确配置
- [ ] 防火墙规则设置
- [ ] 定期安全更新
- [ ] 日志监控设置
- [ ] 备份策略实施
- [ ] 环境变量安全存储
- [ ] API访问限制配置

## 📈 扩展性考虑

### 水平扩展

**1. 负载均衡**

```nginx
upstream travel_tracker {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    location / {
        proxy_pass http://travel_tracker;
    }
}
```

**2. 数据库读写分离**

```python
# 读写分离配置
engines = {
    'writer': create_async_engine(WRITER_DATABASE_URL),
    'reader': create_async_engine(READER_DATABASE_URL)
}
```

### 微服务架构

考虑将系统拆分为独立服务：

- 用户服务
- 旅行计划服务
- 费用服务
- 日志服务
- 通知服务

每个服务独立部署和扩展，通过API网关统一对外提供服务。

这个部署指南涵盖了从开发环境到生产环境的完整部署流程，为不同场景提供了灵活的部署选择。 