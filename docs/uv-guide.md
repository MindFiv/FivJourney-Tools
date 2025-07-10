# uv 使用指南

本项目使用 [uv](https://github.com/astral-sh/uv) 作为 Python 包管理器。uv 是一个极快的 Python 包管理器，用 Rust 编写。

## 为什么选择 uv？

- **极快**：比 pip 快 10-100 倍
- **现代**：原生支持 pyproject.toml
- **可靠**：依赖解析更加准确
- **兼容**：与现有 Python 生态系统完全兼容
- **简单**：更好的用户体验

## 安装 uv

### macOS 和 Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 使用 pip 安装

```bash
pip install uv
```

## 基本命令

### 项目初始化

```bash
# 创建新项目
uv init my-project
cd my-project

# 在现有项目中初始化
uv init
```

### 依赖管理

```bash
# 同步依赖（安装 pyproject.toml 中的依赖）
uv sync

# 同步包含开发依赖
uv sync --extra dev

# 添加新依赖
uv add fastapi
uv add pytest --dev  # 添加开发依赖

# 移除依赖
uv remove package-name

# 更新依赖
uv lock --upgrade
```

### 虚拟环境管理

```bash
# 创建虚拟环境
uv venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 使用特定 Python 版本
uv venv --python 3.10
```

### 运行命令

```bash
# 在虚拟环境中运行命令
uv run python script.py
uv run uvicorn main:app --reload
uv run pytest

# 运行项目脚本（在 pyproject.toml 中定义）
uv run fivjourney-tools
```

## 项目配置

### pyproject.toml

我们的项目使用 `pyproject.toml` 来管理依赖和配置：

```toml
[project]
name = "fivjourney-tools"
dependencies = [
    "fastapi==0.104.1",
    "uvicorn==0.24.0",
    # ... 其他依赖
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "black>=23.0.0",
    # ... 开发依赖
]
```

### uv.toml

项目特定的 uv 配置文件：

```toml
[tool.uv]
index-url = "https://pypi.org/simple"
venv = ".venv"
resolution = "highest"
python = ">=3.10"
```

## 工作流程

### 开发环境设置

```bash
# 1. 克隆项目
git clone <repository-url>
cd fivjourney-tools

# 2. 同步依赖
uv sync --extra dev

# 3. 启动开发服务器
uv run uvicorn main:app --reload
```

### 添加新依赖

```bash
# 添加生产依赖
uv add requests

# 添加开发依赖
uv add pytest --dev

# 添加可选依赖
uv add psycopg2-binary --optional database
```

### 测试和代码质量

```bash
# 运行测试
uv run pytest

# 代码格式化
uv run black app/ main.py
uv run isort app/ main.py

# 类型检查
uv run mypy app/ main.py

# 代码检查
uv run flake8 app/ main.py
```

## 常用命令对比

| 操作 | pip/venv | uv |
|------|----------|-----|
| 创建虚拟环境 | `python -m venv venv` | `uv venv` |
| 激活环境 | `source venv/bin/activate` | 自动管理或 `source .venv/bin/activate` |
| 安装依赖 | `pip install -r requirements.txt` | `uv sync` |
| 添加依赖 | 手动编辑 requirements.txt | `uv add package` |
| 运行脚本 | `python script.py` | `uv run python script.py` |
| 更新依赖 | `pip install --upgrade package` | `uv lock --upgrade` |

## 故障排除

### 常见问题

1. **找不到 Python 版本**
   ```bash
   # 指定 Python 版本
   uv venv --python 3.10
   ```

2. **依赖冲突**
   ```bash
   # 清除缓存
   uv cache clean
   
   # 重新解析依赖
   rm uv.lock
   uv sync
   ```

3. **虚拟环境问题**
   ```bash
   # 删除并重新创建虚拟环境
   rm -rf .venv
   uv venv
   uv sync
   ```

### 调试信息

```bash
# 查看详细信息
uv --verbose sync

# 查看依赖树
uv tree

# 查看配置
uv config
```

## 与传统工具的兼容性

uv 与现有的 Python 生态系统完全兼容：

- 可以读取 `requirements.txt` 文件
- 支持 `setup.py` 和 `setup.cfg`
- 兼容 pip 的命令行参数
- 可以与现有的 CI/CD 流程集成

## 迁移指南

从 pip + requirements.txt 迁移到 uv：

1. 安装 uv
2. 运行 `uv init` 初始化项目
3. 将 requirements.txt 转换为 pyproject.toml
4. 运行 `uv sync` 验证依赖
5. 更新 CI/CD 脚本和文档

## 资源链接

- [uv 官方文档](https://docs.astral.sh/uv/)
- [uv GitHub 仓库](https://github.com/astral-sh/uv)
- [Python Packaging 指南](https://packaging.python.org/) 