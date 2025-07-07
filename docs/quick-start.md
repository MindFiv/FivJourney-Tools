# 快速开始指南

本指南将帮助你快速搭建和运行 FivJourney Tools 旅游全程追踪系统。

## 👨‍💻 作者

**Charlie ZHANG**  
📧 Email: sunnypig2002@gmail.com

## 📋 环境要求

- **Python**: 3.10 或以上版本
- **包管理器**: uv (推荐) 或 pip
- **数据库**: SQLite (默认) 或 PostgreSQL (可选)
- **操作系统**: Windows、macOS、Linux

## 🚀 安装步骤

### 1. 安装 uv (推荐)

选择适合你操作系统的安装方式：

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**使用 pip:**
```bash
pip install uv
```

### 2. 获取项目代码

```bash
git clone <repository-url>
cd fivjourney-tools
```

### 3. 安装项目依赖

**使用 uv (推荐):**
```bash
# 安装生产依赖
uv sync

# 或安装包含开发依赖
uv sync --extra dev
```

**使用传统方式:**
```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate     # Windows

# 安装依赖
pip install -e .
# 或开发依赖
pip install -e .[dev]
```

### 4. 配置环境变量

复制配置文件：
```bash
cp config.env .env
```

编辑 `.env` 文件：
```env
# 数据库配置 (SQLite，无需额外设置)
DATABASE_URL=sqlite:///./travel_tracker.db

# 安全密钥 (请更改为随机字符串)
SECRET_KEY=your-super-secret-key-here-change-me

# 可选配置
DEBUG=True
API_V1_STR=/api/v1
PROJECT_NAME=Travel Tracker
```

## 🔧 启动应用

### 使用 uv (推荐)

```bash
uv run uvicorn main:app --reload
```

### 使用传统方式

```bash
# 确保虚拟环境已激活
python main.py
```

### 使用 Makefile (如果可用)

```bash
make dev
```

## 🌐 访问应用

启动成功后，你可以访问：

- **API 文档 (Swagger)**: http://localhost:8000/docs
- **API 文档 (ReDoc)**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

## 🧪 验证安装

### 1. 健康检查

访问 http://localhost:8000/health，应该看到：
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 2. API 文档

访问 http://localhost:8000/docs，你应该能看到完整的 API 文档界面。

### 3. 注册测试用户

使用 API 文档界面或 curl 命令注册一个测试用户：

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123",
    "full_name": "Test User"
  }'
```

### 4. 登录获取 Token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpassword123"
```

## 🗄️ 数据库配置

### 使用 SQLite (默认)

无需额外配置，系统会自动创建 `travel_tracker.db` 文件。

### 使用 PostgreSQL (可选)

1. 安装 PostgreSQL
2. 创建数据库：
   ```sql
   CREATE DATABASE travel_tracker;
   CREATE USER travel_user WITH PASSWORD 'password';
   GRANT ALL PRIVILEGES ON DATABASE travel_tracker TO travel_user;
   ```

3. 更新 `.env` 文件：
   ```env
   DATABASE_URL=postgresql://travel_user:password@localhost/travel_tracker
   ```

## 🛠️ 开发模式

如果你计划参与开发，建议安装开发依赖：

```bash
# 使用 uv
uv sync --extra dev

# 或使用 pip
pip install -e .[dev]
```

开发工具包括：
- **pytest**: 测试框架
- **black**: 代码格式化
- **isort**: 导入排序
- **flake8**: 代码检查
- **mypy**: 类型检查

使用 Makefile 运行开发任务：
```bash
make test      # 运行测试
make format    # 格式化代码
make lint      # 代码检查
```

## 📱 API 使用示例

### 创建旅行计划

```bash
# 首先获取认证 token (参见上面的登录步骤)
TOKEN="your-jwt-token-here"

# 创建旅行计划
curl -X POST "http://localhost:8000/api/v1/travel-plans/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Tokyo Adventure",
    "description": "A wonderful trip to Tokyo",
    "destination": "Tokyo, Japan",
    "start_date": "2024-06-01",
    "end_date": "2024-06-07",
    "budget": 2000.00
  }'
```

### 获取旅行计划列表

```bash
curl -X GET "http://localhost:8000/api/v1/travel-plans/" \
  -H "Authorization: Bearer $TOKEN"
```

## 🐳 Docker 部署 (可选)

如果你更喜欢使用 Docker：

```bash
# 构建镜像
docker build -t travel-tracker .

# 运行容器
docker run -p 8000:8000 travel-tracker
```

或使用 docker-compose：
```bash
docker-compose up -d
```

## 🔍 故障排除

### 常见问题

1. **端口已被占用**
   ```bash
   # 使用不同端口
   uv run uvicorn main:app --reload --port 8001
   ```

2. **Python 版本不兼容**
   ```bash
   # 检查 Python 版本
   python --version
   # 确保版本 >= 3.10
   ```

3. **依赖安装失败**
   ```bash
   # 清除缓存
   uv cache clean
   # 或
   pip cache purge
   
   # 重新安装
   uv sync
   ```

4. **数据库连接问题**
   - 检查 `.env` 文件中的 `DATABASE_URL`
   - 确保数据库服务正在运行（如果使用 PostgreSQL）

### 获取帮助

如果遇到问题：

1. 查看 [开发指南](./development.md)
2. 检查项目的 Issues 页面
3. 查看日志输出获取错误信息

## 📚 下一步

现在你的系统已经运行，可以：

1. 浏览 [API 文档](./api.md) 了解所有可用端点
2. 查看 [数据模型](./models.md) 了解数据结构
3. 阅读 [开发指南](./development.md) 参与项目开发

祝你使用愉快！🎉 