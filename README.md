# FivJourney Tools

> 🎯 一个基于FastAPI和SQLAlchemy的现代化旅游全程追踪后端系统

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg)](https://sqlalchemy.org)
[![uv](https://img.shields.io/badge/uv-managed-orange.svg)](https://github.com/astral-sh/uv)

为用户提供旅游行前、行中、行后的全过程追踪和帮助的现代化后端系统。

## ✨ 核心特性

🗺️ **旅行计划管理** - 创建、管理完整的旅行计划  
📅 **行程安排** - 详细的日程安排和活动追踪  
💰 **费用记录** - 智能费用分类和统计分析  
📝 **旅行日志** - 记录美好回忆和分享体验  
🔐 **安全认证** - JWT Token + 权限控制  
⚡ **高性能** - 异步API + 现代化技术栈  

## 🚀 快速开始

```bash
# 1. 安装 uv (现代化包管理器)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 克隆项目
git clone <repository-url>
cd fivjourney-tools

# 3. 安装依赖
uv sync --extra dev

# 4. 启动服务
uv run uvicorn main:app --reload
```

🌐 **访问应用:**
- API文档: http://localhost:8000/docs
- API文档(ReDoc): http://localhost:8000/redoc

## 📚 文档目录

| 文档 | 描述 |
|------|------|
| [📖 项目介绍](./docs/README.md) | 系统概述和架构设计 |
| [🚀 快速开始](./docs/quick-start.md) | 详细安装和配置指南 |
| [📱 API文档](./docs/api.md) | 完整的API接口说明 |
| [🛠️ 开发指南](./docs/development.md) | 开发环境和编码规范 |
| [📊 数据模型](./docs/models.md) | 数据库模型详解 |
| [🚢 部署指南](./docs/deployment.md) | 生产环境部署 |
| [⚡ uv使用指南](./docs/uv-guide.md) | 包管理器详细说明 |

> 💡 **提示**: 查看 [docs/index.md](./docs/index.md) 获取完整的文档导航

## 🎯 功能模块

### 🔐 用户管理
- 用户注册、登录、个人信息管理
- JWT Token认证 + 权限控制
- 安全的密码加密存储

### 🗺️ 旅行计划
- 创建和管理旅行计划
- 状态跟踪（计划中→已确认→进行中→已完成）
- 预算管理和成本控制

### 📅 行程安排
- 详细的日程规划
- 多种活动类型（交通、住宿、观光、用餐、购物、娱乐）
- 地理位置和时间管理

### 💰 费用记录
- 智能分类费用记录
- 多货币支持和汇率转换
- 详细的统计分析和报表

### 📝 旅行日志
- 记录旅行见闻和感受
- 图片和标签管理
- 灵活的隐私设置（私人/公开/朋友可见）

## 🛠️ 技术栈

- **后端框架**: FastAPI (异步高性能)
- **数据库ORM**: SQLAlchemy 2.0 (异步)
- **数据验证**: Pydantic
- **认证**: JWT + bcrypt
- **包管理**: uv (极速包管理器)
- **数据库**: SQLite/PostgreSQL
- **容器化**: Docker + Docker Compose

## 📊 项目状态

- ✅ 用户认证系统
- ✅ 旅行计划管理
- ✅ 行程安排功能
- ✅ 费用记录统计
- ✅ 旅行日志系统
- ✅ API文档生成
- ✅ Docker容器化
- 🚧 单元测试完善中
- 📋 移动端API优化计划中

## 🤝 贡献

我们欢迎社区贡献！请参阅：

1. [开发指南](./docs/development.md) - 开发环境配置
2. [编码规范](./docs/coding-standards.md) - 代码风格指南
3. [贡献指南](./docs/contributing.md) - 贡献流程说明

## 👨‍💻 作者

**Charlie ZHANG**  
📧 Email: sunnypig2002@gmail.com

## 📞 支持

- 📖 [完整文档](./docs/index.md)
- 🐛 [问题反馈](https://github.com/your-repo/issues)
- 💬 [讨论区](https://github.com/your-repo/discussions)

## 📄 许可证

本项目采用 [MIT License](./LICENSE) 开源协议。

---

<div align="center">

**🎉 让每次旅行都变得更加有序、有趣、有意义！**

[开始使用](./docs/quick-start.md) • [查看文档](./docs/index.md) • [API文档](http://localhost:8000/docs)

</div> 