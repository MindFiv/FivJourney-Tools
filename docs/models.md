# 数据模型文档

本文档详细描述 FivJourney Tools 旅游全程追踪系统的数据库模型设计和关系。

## 👨‍💻 作者

**Charlie ZHANG**  
📧 Email: sunnypig2002@gmail.com

## 📊 数据库设计概览

系统采用关系型数据库设计，支持SQLite（开发环境）和PostgreSQL（生产环境）。核心实体包括用户、旅行计划、行程安排、费用记录和旅行日志。

### ER 图概述

```
User (用户)
├── TravelPlan (旅行计划) [1:N]
    ├── Itinerary (行程安排) [1:N]
    ├── Expense (费用记录) [1:N]
    └── TravelLog (旅行日志) [1:N]
```

## 🏗️ 核心模型

### 1. User (用户模型)

用户认证和个人信息管理。

```python
# app/models/user.py
class User(Base):
    __tablename__ = "users"
    
    # 基本字段
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # 个人信息
    full_name = Column(String(100))
    avatar_url = Column(String(255))
    bio = Column(Text)
    
    # 账户状态
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    travel_plans = relationship("TravelPlan", back_populates="user", cascade="all, delete-orphan")
```

**字段说明：**

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| `id` | Integer | 主键ID | PK, 自增 |
| `username` | String(50) | 用户名 | 唯一, 非空, 索引 |
| `email` | String(100) | 邮箱 | 唯一, 非空, 索引 |
| `hashed_password` | String(255) | 加密密码 | 非空 |
| `full_name` | String(100) | 真实姓名 | 可空 |
| `avatar_url` | String(255) | 头像URL | 可空 |
| `bio` | Text | 个人简介 | 可空 |
| `is_active` | Boolean | 账户是否激活 | 默认True |
| `is_verified` | Boolean | 邮箱是否验证 | 默认False |
| `created_at` | DateTime | 创建时间 | 自动设置 |
| `updated_at` | DateTime | 更新时间 | 自动更新 |

#### 索引策略

```sql
-- 复合索引：邮箱和激活状态
CREATE INDEX idx_user_email_active ON users(email, is_active);

-- 用户名索引（用于登录）
CREATE INDEX idx_user_username ON users(username);
```

### 2. TravelPlan (旅行计划模型)

旅行计划的核心信息和状态管理。

```python
# app/models/travel_plan.py
from enum import Enum

class PlanStatus(str, Enum):
    PLANNING = "planning"        # 计划中
    CONFIRMED = "confirmed"      # 已确认
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"      # 已完成
    CANCELLED = "cancelled"      # 已取消

class TravelPlan(Base):
    __tablename__ = "travel_plans"
    
    # 基本信息
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    destination = Column(String(100), nullable=False, index=True)
    
    # 时间安排
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False)
    
    # 预算信息
    budget = Column(DECIMAL(10, 2))
    currency = Column(String(3), default="CNY")  # ISO 货币代码
    
    # 状态管理
    status = Column(Enum(PlanStatus), default=PlanStatus.PLANNING, index=True)
    
    # 分享设置
    is_public = Column(Boolean, default=False)
    share_code = Column(String(20), unique=True)  # 分享码
    
    # 外键
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    user = relationship("User", back_populates="travel_plans")
    itineraries = relationship("Itinerary", back_populates="travel_plan", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="travel_plan", cascade="all, delete-orphan")
    travel_logs = relationship("TravelLog", back_populates="travel_plan", cascade="all, delete-orphan")
```

#### 字段说明

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| `id` | Integer | 主键ID | PK, 自增 |
| `title` | String(200) | 计划标题 | 非空 |
| `description` | Text | 详细描述 | 可空 |
| `destination` | String(100) | 目的地 | 非空, 索引 |
| `start_date` | Date | 开始日期 | 非空, 索引 |
| `end_date` | Date | 结束日期 | 非空 |
| `budget` | DECIMAL(10,2) | 预算金额 | 可空 |
| `currency` | String(3) | 货币代码 | 默认CNY |
| `status` | Enum | 计划状态 | 索引 |
| `is_public` | Boolean | 是否公开 | 默认False |
| `share_code` | String(20) | 分享码 | 唯一 |
| `user_id` | Integer | 用户ID | FK, 非空, 索引 |

#### 状态转换规则

```python
# 允许的状态转换
ALLOWED_STATUS_TRANSITIONS = {
    PlanStatus.PLANNING: [PlanStatus.CONFIRMED, PlanStatus.CANCELLED],
    PlanStatus.CONFIRMED: [PlanStatus.IN_PROGRESS, PlanStatus.CANCELLED],
    PlanStatus.IN_PROGRESS: [PlanStatus.COMPLETED, PlanStatus.CANCELLED],
    PlanStatus.COMPLETED: [],  # 完成状态不能转换
    PlanStatus.CANCELLED: [PlanStatus.PLANNING]  # 取消后可重新规划
}
```

### 3. Itinerary (行程安排模型)

详细的行程安排和活动记录。

```python
# app/models/itinerary.py
class ActivityType(str, Enum):
    TRANSPORT = "transport"      # 交通
    ACCOMMODATION = "accommodation"  # 住宿
    SIGHTSEEING = "sightseeing"  # 观光
    DINING = "dining"           # 用餐
    SHOPPING = "shopping"       # 购物
    ENTERTAINMENT = "entertainment"  # 娱乐
    OTHER = "other"             # 其他

class Itinerary(Base):
    __tablename__ = "itineraries"
    
    # 基本信息
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    activity_type = Column(Enum(ActivityType), nullable=False, index=True)
    
    # 时间安排
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True))
    
    # 地理位置
    location = Column(String(200))
    latitude = Column(Float)   # 纬度
    longitude = Column(Float)  # 经度
    address = Column(String(300))
    
    # 费用信息
    estimated_cost = Column(DECIMAL(10, 2))
    actual_cost = Column(DECIMAL(10, 2))
    
    # 预订信息
    booking_reference = Column(String(100))  # 预订参考号
    booking_status = Column(String(50))      # 预订状态
    
    # 备注
    notes = Column(Text)
    
    # 外键
    travel_plan_id = Column(Integer, ForeignKey("travel_plans.id"), nullable=False, index=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    travel_plan = relationship("TravelPlan", back_populates="itineraries")
```

#### 字段说明

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| `id` | Integer | 主键ID | PK, 自增 |
| `title` | String(200) | 活动标题 | 非空 |
| `description` | Text | 活动描述 | 可空 |
| `activity_type` | Enum | 活动类型 | 非空, 索引 |
| `start_time` | DateTime | 开始时间 | 非空, 索引 |
| `end_time` | DateTime | 结束时间 | 可空 |
| `location` | String(200) | 地点名称 | 可空 |
| `latitude` | Float | 纬度 | 可空 |
| `longitude` | Float | 经度 | 可空 |
| `address` | String(300) | 详细地址 | 可空 |
| `estimated_cost` | DECIMAL(10,2) | 预估费用 | 可空 |
| `actual_cost` | DECIMAL(10,2) | 实际费用 | 可空 |
| `booking_reference` | String(100) | 预订号 | 可空 |
| `booking_status` | String(50) | 预订状态 | 可空 |
| `notes` | Text | 备注 | 可空 |
| `travel_plan_id` | Integer | 旅行计划ID | FK, 非空, 索引 |

### 4. Expense (费用记录模型)

详细的费用记录和分类统计。

```python
# app/models/expense.py
class ExpenseCategory(str, Enum):
    TRANSPORT = "transport"      # 交通费
    ACCOMMODATION = "accommodation"  # 住宿费
    FOOD = "food"               # 餐饮费
    TICKETS = "tickets"         # 门票费
    SHOPPING = "shopping"       # 购物费
    ENTERTAINMENT = "entertainment"  # 娱乐费
    INSURANCE = "insurance"     # 保险费
    VISA = "visa"              # 签证费
    OTHER = "other"            # 其他费用

class Expense(Base):
    __tablename__ = "expenses"
    
    # 基本信息
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(Enum(ExpenseCategory), nullable=False, index=True)
    
    # 金额信息
    amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), default="CNY")
    exchange_rate = Column(DECIMAL(10, 4), default=1.0)  # 汇率
    amount_in_base_currency = Column(DECIMAL(10, 2))  # 基础货币金额
    
    # 时间和地点
    expense_date = Column(Date, nullable=False, index=True)
    location = Column(String(200))
    
    # 支付信息
    payment_method = Column(String(50))  # 支付方式
    receipt_url = Column(String(500))    # 发票URL
    
    # 外键
    travel_plan_id = Column(Integer, ForeignKey("travel_plans.id"), nullable=False, index=True)
    itinerary_id = Column(Integer, ForeignKey("itineraries.id"), nullable=True, index=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    travel_plan = relationship("TravelPlan", back_populates="expenses")
    itinerary = relationship("Itinerary")
```

#### 字段说明

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| `id` | Integer | 主键ID | PK, 自增 |
| `title` | String(200) | 费用标题 | 非空 |
| `description` | Text | 费用描述 | 可空 |
| `category` | Enum | 费用类别 | 非空, 索引 |
| `amount` | DECIMAL(10,2) | 金额 | 非空 |
| `currency` | String(3) | 货币代码 | 默认CNY |
| `exchange_rate` | DECIMAL(10,4) | 汇率 | 默认1.0 |
| `amount_in_base_currency` | DECIMAL(10,2) | 基础货币金额 | 可空 |
| `expense_date` | Date | 费用日期 | 非空, 索引 |
| `location` | String(200) | 消费地点 | 可空 |
| `payment_method` | String(50) | 支付方式 | 可空 |
| `receipt_url` | String(500) | 发票URL | 可空 |
| `travel_plan_id` | Integer | 旅行计划ID | FK, 非空, 索引 |
| `itinerary_id` | Integer | 行程ID | FK, 可空, 索引 |

### 5. TravelLog (旅行日志模型)

旅行期间的日志记录和分享。

```python
# app/models/travel_log.py
class PrivacyLevel(str, Enum):
    PRIVATE = "private"    # 私人
    PUBLIC = "public"      # 公开
    FRIENDS = "friends"    # 朋友可见

class TravelLog(Base):
    __tablename__ = "travel_logs"
    
    # 基本信息
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    
    # 地理和时间信息
    location = Column(String(200))
    latitude = Column(Float)
    longitude = Column(Float)
    log_date = Column(Date, nullable=False, index=True)
    
    # 多媒体内容
    images = Column(JSON)  # 存储图片URL列表
    weather = Column(String(100))  # 天气情况
    temperature = Column(Float)    # 温度
    
    # 情感记录
    mood = Column(String(50))      # 心情
    rating = Column(Integer)       # 评分 1-5
    
    # 隐私设置
    privacy_level = Column(Enum(PrivacyLevel), default=PrivacyLevel.PRIVATE, index=True)
    
    # 社交功能
    likes_count = Column(Integer, default=0)
    views_count = Column(Integer, default=0)
    
    # 外键
    travel_plan_id = Column(Integer, ForeignKey("travel_plans.id"), nullable=False, index=True)
    itinerary_id = Column(Integer, ForeignKey("itineraries.id"), nullable=True, index=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    travel_plan = relationship("TravelPlan", back_populates="travel_logs")
    itinerary = relationship("Itinerary")
```

#### 字段说明

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| `id` | Integer | 主键ID | PK, 自增 |
| `title` | String(200) | 日志标题 | 非空 |
| `content` | Text | 日志内容 | 非空 |
| `location` | String(200) | 地点 | 可空 |
| `latitude` | Float | 纬度 | 可空 |
| `longitude` | Float | 经度 | 可空 |
| `log_date` | Date | 日志日期 | 非空, 索引 |
| `images` | JSON | 图片列表 | 可空 |
| `weather` | String(100) | 天气 | 可空 |
| `temperature` | Float | 温度 | 可空 |
| `mood` | String(50) | 心情 | 可空 |
| `rating` | Integer | 评分(1-5) | 可空 |
| `privacy_level` | Enum | 隐私级别 | 索引, 默认private |
| `likes_count` | Integer | 点赞数 | 默认0 |
| `views_count` | Integer | 浏览数 | 默认0 |
| `travel_plan_id` | Integer | 旅行计划ID | FK, 非空, 索引 |
| `itinerary_id` | Integer | 行程ID | FK, 可空, 索引 |

## 🔗 关系设计

### 主要关系

1. **User ←→ TravelPlan** (一对多)
   - 一个用户可以创建多个旅行计划
   - 每个旅行计划属于一个用户

2. **TravelPlan ←→ Itinerary** (一对多)
   - 一个旅行计划包含多个行程安排
   - 每个行程属于一个旅行计划

3. **TravelPlan ←→ Expense** (一对多)
   - 一个旅行计划包含多个费用记录
   - 每个费用记录属于一个旅行计划

4. **TravelPlan ←→ TravelLog** (一对多)
   - 一个旅行计划包含多个旅行日志
   - 每个旅行日志属于一个旅行计划

5. **Itinerary ←→ Expense** (一对多，可选)
   - 费用记录可以关联到具体的行程安排
   - 行程安排可以有多个相关费用

6. **Itinerary ←→ TravelLog** (一对多，可选)
   - 旅行日志可以关联到具体的行程安排
   - 行程安排可以有多个相关日志

### 外键约束

```sql
-- 旅行计划表外键
ALTER TABLE travel_plans ADD CONSTRAINT fk_travel_plan_user 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- 行程表外键
ALTER TABLE itineraries ADD CONSTRAINT fk_itinerary_travel_plan 
    FOREIGN KEY (travel_plan_id) REFERENCES travel_plans(id) ON DELETE CASCADE;

-- 费用表外键
ALTER TABLE expenses ADD CONSTRAINT fk_expense_travel_plan 
    FOREIGN KEY (travel_plan_id) REFERENCES travel_plans(id) ON DELETE CASCADE;

ALTER TABLE expenses ADD CONSTRAINT fk_expense_itinerary 
    FOREIGN KEY (itinerary_id) REFERENCES itineraries(id) ON DELETE SET NULL;

-- 旅行日志表外键
ALTER TABLE travel_logs ADD CONSTRAINT fk_travel_log_travel_plan 
    FOREIGN KEY (travel_plan_id) REFERENCES travel_plans(id) ON DELETE CASCADE;

ALTER TABLE travel_logs ADD CONSTRAINT fk_travel_log_itinerary 
    FOREIGN KEY (itinerary_id) REFERENCES itineraries(id) ON DELETE SET NULL;
```

## 📈 索引策略

### 主要索引

```sql
-- 用户表索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_is_active ON users(is_active);

-- 旅行计划表索引
CREATE INDEX idx_travel_plans_user_id ON travel_plans(user_id);
CREATE INDEX idx_travel_plans_destination ON travel_plans(destination);
CREATE INDEX idx_travel_plans_start_date ON travel_plans(start_date);
CREATE INDEX idx_travel_plans_status ON travel_plans(status);
CREATE INDEX idx_travel_plans_is_public ON travel_plans(is_public);

-- 行程表索引
CREATE INDEX idx_itineraries_travel_plan_id ON itineraries(travel_plan_id);
CREATE INDEX idx_itineraries_start_time ON itineraries(start_time);
CREATE INDEX idx_itineraries_activity_type ON itineraries(activity_type);

-- 费用表索引
CREATE INDEX idx_expenses_travel_plan_id ON expenses(travel_plan_id);
CREATE INDEX idx_expenses_category ON expenses(category);
CREATE INDEX idx_expenses_date ON expenses(expense_date);

-- 旅行日志表索引
CREATE INDEX idx_travel_logs_travel_plan_id ON travel_logs(travel_plan_id);
CREATE INDEX idx_travel_logs_date ON travel_logs(log_date);
CREATE INDEX idx_travel_logs_privacy ON travel_logs(privacy_level);

-- 复合索引
CREATE INDEX idx_travel_plans_user_status ON travel_plans(user_id, status);
CREATE INDEX idx_expenses_plan_category ON expenses(travel_plan_id, category);
CREATE INDEX idx_travel_logs_plan_privacy ON travel_logs(travel_plan_id, privacy_level);
```

### 地理位置索引

```sql
-- 为地理位置字段创建空间索引（PostgreSQL）
CREATE INDEX idx_itineraries_location ON itineraries USING GIST (ST_Point(longitude, latitude));
CREATE INDEX idx_travel_logs_location ON travel_logs USING GIST (ST_Point(longitude, latitude));
```

## 🔄 数据库迁移

### Alembic 配置

```python
# alembic/env.py
from app.models import Base
target_metadata = Base.metadata

# 生成迁移文件
alembic revision --autogenerate -m "初始化数据库模型"

# 执行迁移
alembic upgrade head
```

### 常见迁移场景

```python
# 添加新字段
def upgrade():
    op.add_column('travel_plans', sa.Column('tags', sa.JSON(), nullable=True))

# 修改字段类型
def upgrade():
    op.alter_column('expenses', 'amount', type_=sa.DECIMAL(12, 2))

# 添加索引
def upgrade():
    op.create_index('idx_travel_plans_tags', 'travel_plans', ['tags'])

# 数据迁移
def upgrade():
    connection = op.get_bind()
    connection.execute(
        "UPDATE travel_plans SET currency = 'CNY' WHERE currency IS NULL"
    )
```

## 📊 数据完整性

### 约束规则

```sql
-- 检查约束
ALTER TABLE travel_plans ADD CONSTRAINT check_travel_plan_dates 
    CHECK (end_date >= start_date);

ALTER TABLE expenses ADD CONSTRAINT check_expense_amount 
    CHECK (amount >= 0);

ALTER TABLE travel_logs ADD CONSTRAINT check_travel_log_rating 
    CHECK (rating >= 1 AND rating <= 5);

ALTER TABLE itineraries ADD CONSTRAINT check_itinerary_times 
    CHECK (end_time IS NULL OR end_time >= start_time);

-- 唯一约束
ALTER TABLE travel_plans ADD CONSTRAINT unique_share_code 
    UNIQUE (share_code);
```

### 触发器示例

```sql
-- 自动更新统计信息
CREATE OR REPLACE FUNCTION update_plan_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- 更新旅行计划的总费用
    UPDATE travel_plans 
    SET total_expense = (
        SELECT COALESCE(SUM(amount), 0) 
        FROM expenses 
        WHERE travel_plan_id = NEW.travel_plan_id
    )
    WHERE id = NEW.travel_plan_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_plan_stats
    AFTER INSERT OR UPDATE OR DELETE ON expenses
    FOR EACH ROW EXECUTE FUNCTION update_plan_stats();
```

## 🎯 性能优化建议

### 查询优化

1. **使用适当的预加载**
   ```python
   # 预加载相关数据
   plans = await db.execute(
       select(TravelPlan)
       .options(
           selectinload(TravelPlan.itineraries),
           selectinload(TravelPlan.expenses)
       )
       .where(TravelPlan.user_id == user_id)
   )
   ```

2. **分页查询**
   ```python
   # 分页获取数据
   def paginate(query, page: int, size: int):
       offset = (page - 1) * size
       return query.offset(offset).limit(size)
   ```

3. **索引优化**
   - 为经常查询的字段添加索引
   - 使用复合索引覆盖多字段查询
   - 定期分析查询性能

### 数据归档

```python
# 归档完成的旅行计划
async def archive_completed_plans():
    cutoff_date = datetime.now() - timedelta(days=365)  # 一年前
    
    old_plans = await db.execute(
        select(TravelPlan)
        .where(
            TravelPlan.status == PlanStatus.COMPLETED,
            TravelPlan.end_date < cutoff_date
        )
    )
    
    # 移动到归档表或标记为归档
    for plan in old_plans.scalars():
        plan.is_archived = True
```

这个数据模型设计为旅游追踪系统提供了完整的数据基础，支持从计划制定到旅行记录的全过程管理。 