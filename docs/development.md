# 开发指南

本文档为参与 FivJourney Tools 旅游全程追踪系统开发的开发者提供详细的开发指南。

## 👨‍💻 作者

**Charlie ZHANG**  
📧 Email: sunnypig2002@gmail.com

## 🛠️ 开发环境配置

### 环境要求

- **Python**: 3.10 或以上版本
- **Git**: 版本控制
- **uv**: 包管理器 (推荐)
- **IDE**: VS Code、PyCharm 或其他Python IDE
- **数据库**: SQLite (开发) / PostgreSQL (生产)

### 初始设置

```bash
# 1. 克隆项目
git clone <repository-url>
cd fivjourney-tools

# 2. 安装 uv (如果尚未安装)
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
# 或
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows

# 3. 安装开发依赖
uv sync --extra dev

# 4. 配置环境变量
cp config.env .env
# 编辑 .env 文件配置数据库等设置

# 5. 运行测试确保环境正常
uv run pytest

# 6. 启动开发服务器
uv run uvicorn main:app --reload
```

### IDE 配置

#### VS Code 推荐配置

创建 `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "./.venv/bin/python",
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length=120"],
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.flake8Args": ["--max-line-length=120"],
  "python.linting.mypyEnabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

推荐扩展：
- Python
- Python Docstring Generator
- GitLens
- REST Client
- SQLite Viewer

## 📋 编码规范

### Python 代码规范

遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 和项目特定规范：

#### 基本规范

```python
# 1. 导入顺序
# 标准库
from datetime import datetime
from typing import Optional, List

# 第三方库
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

# 本地导入
from app.core.database import get_db
from app.models.user import User

# 2. 类型提示
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """创建新用户
    
    Args:
        user_data: 用户创建数据
        db: 数据库会话
        
    Returns:
        UserResponse: 创建的用户信息
    """
    pass

# 3. 异常处理
if not user:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="用户不存在"
    )
```

#### 命名规范

- **文件名**: snake_case (例: `user_service.py`)
- **类名**: PascalCase (例: `UserService`)
- **函数名**: snake_case (例: `get_user_by_id`)
- **变量名**: snake_case (例: `user_id`)
- **常量**: UPPER_CASE (例: `SECRET_KEY`)

#### 文档字符串

使用中文文档字符串，便于团队理解：

```python
async def update_travel_plan(
    plan_id: int,
    plan_data: TravelPlanUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> TravelPlanResponse:
    """更新旅行计划
    
    更新指定ID的旅行计划信息。只有计划的创建者才能更新。
    
    Args:
        plan_id: 旅行计划ID
        plan_data: 更新数据
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        TravelPlanResponse: 更新后的旅行计划信息
        
    Raises:
        HTTPException: 计划不存在或无权限时抛出异常
        
    Example:
        ```python
        plan = await update_travel_plan(
            plan_id=1,
            plan_data=TravelPlanUpdate(title="新标题"),
            current_user=user,
            db=db
        )
        ```
    """
```

### 代码格式化

使用以下工具进行代码格式化：

```bash
# 代码格式化
uv run black app/ main.py --line-length 120

# 导入排序
uv run isort app/ main.py

# 代码检查
uv run flake8 app/ main.py --max-line-length 120

# 类型检查
uv run mypy app/ main.py

# 或使用 Makefile
make format  # 格式化
make lint    # 检查
```

## 🏗️ 项目架构

### 目录结构

```
app/
├── __init__.py
├── api/v1/                  # API 路由
│   ├── __init__.py
│   ├── router.py           # 主路由汇总
│   └── endpoints/          # 具体端点
│       ├── auth.py         # 认证相关
│       ├── users.py        # 用户管理
│       ├── travel_plans.py # 旅行计划
│       ├── itineraries.py  # 行程安排
│       ├── expenses.py     # 费用记录
│       └── travel_logs.py  # 旅行日志
├── core/                   # 核心配置
│   ├── config.py          # 配置管理
│   ├── database.py        # 数据库配置
│   └── security.py        # 安全认证
├── models/                 # SQLAlchemy 模型
│   ├── __init__.py
│   ├── user.py           # 用户模型
│   ├── travel_plan.py    # 旅行计划模型
│   ├── itinerary.py      # 行程模型
│   ├── expense.py        # 费用模型
│   └── travel_log.py     # 日志模型
└── schemas/               # Pydantic 模型
    ├── __init__.py
    ├── user.py           # 用户模式
    ├── travel_plan.py    # 旅行计划模式
    ├── itinerary.py      # 行程模式
    ├── expense.py        # 费用模式
    └── travel_log.py     # 日志模式
```

### 设计模式

#### 依赖注入

```python
# 数据库依赖
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session

# 认证依赖
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    # 验证token并返回用户
    pass

# 在端点中使用
@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    return current_user
```

#### 仓库模式 (Repository Pattern)

```python
# app/repositories/user_repository.py
class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def create(self, user_data: UserCreate) -> User:
        user = User(**user_data.dict())
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

# 在端点中使用
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    repo = UserRepository(db)
    return await repo.create(user_data)
```

## 🧪 测试指南

### 测试结构

```
tests/
├── __init__.py
├── conftest.py           # 测试配置和固定装置
├── test_auth.py         # 认证测试
├── test_users.py        # 用户测试
├── test_travel_plans.py # 旅行计划测试
├── test_itineraries.py  # 行程测试
├── test_expenses.py     # 费用测试
└── test_travel_logs.py  # 日志测试
```

### 测试配置

创建 `tests/conftest.py`:

```python
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import get_db
from app.models import Base
from main import app

# 测试数据库配置
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def async_client():
    # 创建测试数据库
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    TestingSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()
```

### 编写测试

```python
# tests/test_travel_plans.py
import pytest
from httpx import AsyncClient

class TestTravelPlans:
    async def test_create_travel_plan(self, async_client: AsyncClient):
        """测试创建旅行计划"""
        # 先注册和登录用户
        register_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "full_name": "Test User"
        }
        await async_client.post("/api/v1/auth/register", json=register_data)
        
        login_data = {
            "username": "testuser",
            "password": "testpass123"
        }
        login_response = await async_client.post(
            "/api/v1/auth/login", 
            data=login_data
        )
        token = login_response.json()["access_token"]
        
        # 创建旅行计划
        plan_data = {
            "title": "Tokyo Trip",
            "description": "A wonderful trip to Tokyo",
            "destination": "Tokyo, Japan",
            "start_date": "2024-06-01",
            "end_date": "2024-06-07",
            "budget": 2000.00
        }
        
        response = await async_client.post(
            "/api/v1/travel-plans/",
            json=plan_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Tokyo Trip"
        assert data["destination"] == "Tokyo, Japan"

    async def test_get_travel_plans(self, async_client: AsyncClient):
        """测试获取旅行计划列表"""
        # 实现测试逻辑
        pass
```

### 运行测试

```bash
# 运行所有测试
uv run pytest

# 运行特定测试文件
uv run pytest tests/test_travel_plans.py

# 运行特定测试函数
uv run pytest tests/test_travel_plans.py::TestTravelPlans::test_create_travel_plan

# 生成测试覆盖率报告
uv run pytest --cov=app --cov-report=html

# 使用 Makefile
make test      # 运行测试
make test-cov  # 测试覆盖率
```

## 🔄 开发工作流程

### Git 工作流

#### 分支策略

- `main`: 主分支，生产环境代码
- `develop`: 开发分支，集成最新功能
- `feature/*`: 功能分支
- `bugfix/*`: 错误修复分支
- `hotfix/*`: 紧急修复分支

#### 提交规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```bash
# 功能
git commit -m "feat: 添加旅行计划状态更新功能"

# 修复
git commit -m "fix: 修复费用统计计算错误"

# 文档
git commit -m "docs: 更新API文档"

# 样式
git commit -m "style: 格式化代码"

# 重构
git commit -m "refactor: 重构用户认证逻辑"

# 测试
git commit -m "test: 添加旅行计划单元测试"

# 构建
git commit -m "build: 更新依赖版本"
```

### 开发流程

1. **创建功能分支**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/travel-plan-sharing
   ```

2. **开发和测试**
   ```bash
   # 编写代码
   # 运行测试
   uv run pytest
   
   # 格式化代码
   make format
   
   # 代码检查
   make lint
   ```

3. **提交更改**
   ```bash
   git add .
   git commit -m "feat: 添加旅行计划分享功能"
   git push origin feature/travel-plan-sharing
   ```

4. **创建 Pull Request**
   - 在 GitHub/GitLab 上创建 PR
   - 详细描述更改内容
   - 确保通过 CI 检查
   - 等待代码审查

### 代码审查

#### 审查清单

- [ ] 代码符合项目编码规范
- [ ] 有充分的测试覆盖
- [ ] 有适当的文档和注释
- [ ] 性能考虑合理
- [ ] 安全性检查通过
- [ ] API 设计遵循 RESTful 原则
- [ ] 错误处理恰当
- [ ] 数据库查询优化

## 🚀 性能优化

### 数据库优化

```python
# 1. 使用合适的索引
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)  # 邮箱索引
    username = Column(String, unique=True, index=True)  # 用户名索引

# 2. 避免 N+1 查询
# 错误方式
plans = await db.execute(select(TravelPlan))
for plan in plans.scalars():
    expenses = await db.execute(
        select(Expense).where(Expense.travel_plan_id == plan.id)
    )

# 正确方式
plans = await db.execute(
    select(TravelPlan).options(selectinload(TravelPlan.expenses))
)

# 3. 分页查询
def paginate_query(query, page: int = 1, size: int = 10):
    offset = (page - 1) * size
    return query.offset(offset).limit(size)
```

### API 优化

```python
# 1. 异步处理
@router.post("/travel-plans/")
async def create_travel_plan(
    plan_data: TravelPlanCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    plan = await create_plan(plan_data, current_user, db)
    
    # 后台任务发送邮件通知
    background_tasks.add_task(send_plan_created_email, plan, current_user)
    
    return plan

# 2. 缓存
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache

@router.get("/travel-plans/{plan_id}")
@cache(expire=300)  # 缓存5分钟
async def get_travel_plan(plan_id: int):
    # 实现逻辑
    pass
```

## 🐛 调试指南

### 日志配置

```python
# app/core/logging.py
import logging
from app.core.config import settings

# 配置日志
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# 在代码中使用
logger.info(f"用户 {user.username} 创建了旅行计划 {plan.title}")
logger.error(f"创建旅行计划失败: {str(e)}")
```

### 调试技巧

```python
# 1. 使用 pdb 调试
import pdb; pdb.set_trace()

# 2. 异步调试
import asyncio
async def debug_async():
    breakpoint()  # Python 3.7+

# 3. 打印 SQL 查询
# 在 database.py 中设置 echo=True
engine = create_async_engine(DATABASE_URL, echo=True)
```

## 📝 贡献指南

### 如何贡献

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 创建 Pull Request

### 贡献类型

- 🐛 Bug 修复
- ✨ 新功能
- 📝 文档改进
- 🎨 代码优化
- 🧪 测试增强

## 🔗 相关资源

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 文档](https://docs.sqlalchemy.org/en/20/)
- [Pydantic 文档](https://pydantic-docs.helpmanual.io/)
- [uv 文档](https://docs.astral.sh/uv/)
- [Python 异步编程指南](https://docs.python.org/3/library/asyncio.html) 