# FivJourney Tools 文档

欢迎使用 FivJourney Tools！这是一个基于FastAPI和SQLAlchemy的现代化旅游全程追踪后端系统。

## 👨‍💻 作者

**Charlie ZHANG**  
📧 Email: sunnypig2002@gmail.com

## 📚 文档导航

- [项目介绍](./README.md) - 系统概述和功能特性
- [快速开始](./quick-start.md) - 安装和基本使用
- [API文档](./api.md) - 详细的API接口说明
- [开发指南](./development.md) - 开发环境配置和编码规范 ✅
- [数据库模型](./models.md) - 数据模型说明 ✅
- [部署指南](./deployment.md) - 生产环境部署 ✅
- [代码质量指南](./lint-guide.md) - Lint工具和代码格式化 ✅
- [uv使用指南](./uv-guide.md) - 包管理器使用说明

## 🚀 系统特色

- **全程追踪**：覆盖旅游计划、行程安排、费用记录、旅行日志
- **现代技术栈**：FastAPI + SQLAlchemy 2.0 + uv 包管理
- **安全认证**：JWT Token + bcrypt 密码加密
- **数据分析**：费用统计、行程优化、数据可视化
- **API优先**：完整的RESTful API + 自动文档生成

## 🔧 技术栈

- **后端框架**: FastAPI (异步)
- **数据库**: SQLAlchemy 2.0 (异步ORM)
- **数据验证**: Pydantic
- **认证**: JWT + bcrypt
- **包管理**: uv (推荐)
- **数据库**: SQLite/PostgreSQL

## 📋 核心功能

### 用户管理
- 用户注册和登录
- 个人信息管理
- 权限控制

### 旅行计划
- 创建和管理旅行计划
- 状态跟踪（计划中→已确认→进行中→已完成）
- 预算管理

### 行程安排
- 详细的日程安排
- 多种活动类型（交通、住宿、观光、用餐、购物、娱乐）
- 地理位置信息

### 费用记录
- 分类费用记录
- 统计分析
- 多货币支持

### 旅行日志
- 记录旅行见闻
- 图片和标签
- 隐私设置（私人/公开/朋友可见）

## 🎯 快速开始

1. **安装 uv**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
```

2. **安装依赖**
```bash
uv sync --extra dev
```

3. **启动服务**
```bash
uv run uvicorn main:app --reload
```

4. **访问文档**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📞 获取帮助

如果你在使用过程中遇到问题，可以：

1. 查看相关文档章节
2. 检查 [常见问题](./faq.md)
3. 提交 Issue

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](../LICENSE) 文件。 