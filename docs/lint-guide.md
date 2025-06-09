# 代码质量和Lint指南

本指南详细介绍如何使用项目中的代码质量工具进行格式化、检查和优化。

## 🛠️ 可用工具

### 格式化工具

- **Black**: Python代码格式化器，自动格式化代码风格
- **isort**: 导入语句排序和组织
- **autoflake**: 删除未使用的导入和变量

### 代码检查工具

- **flake8**: PEP 8 风格检查和代码质量检查
- **mypy**: 静态类型检查
- **bandit**: 安全漏洞检查
- **safety**: 依赖安全性检查

## 📋 可用命令

### 基础命令

```bash
# 格式化代码 (会修改文件)
make format

# 检查代码格式 (不修改文件)
make format-check

# 代码质量检查
make lint

# 安全检查
make security
```

### 高级命令

```bash
# 高级代码清理 (删除未使用导入 + 升级语法 + 格式化)
make format-advanced

# 完整检查 (格式化 + 检查)
make check

# 严格检查 (不修改文件)
make check-strict

# 全面检查 (包括安全和测试)
make check-all

# CI/CD检查 (适用于持续集成)
make ci-check
```

### Pre-commit钩子

```bash
# 安装pre-commit钩子 (在git commit前自动运行检查)
make pre-commit-install

# 手动运行pre-commit检查
make pre-commit-run

# 更新pre-commit钩子版本
make pre-commit-update
```

## 🔧 详细说明

### 1. 代码格式化

#### make format
自动格式化所有Python代码，包括：
- 使用Black格式化代码风格（行长度120字符）
- 使用isort排序和组织导入语句

```bash
$ make format
🔧 正在格式化代码...
reformatted app/core/config.py
reformatted main.py
Fixing import app/models/user.py
✅ 代码格式化完成
```

#### make format-check
检查代码格式是否符合规范，但不修改文件：

```bash
$ make format-check
🔍 检查代码格式...
All done! ✨ 🍰 ✨
2 files would be left unchanged.
Skipped 1 files
✅ 代码格式检查完成
```

#### make format-advanced
高级代码清理，包括：
- 删除未使用的导入（autoflake）
- 升级Python语法到3.10+（pyupgrade）
- 代码格式化（black + isort）

### 2. 代码质量检查

#### make lint
运行代码质量检查：

```bash
$ make lint
🔍 正在进行代码检查...
📋 运行 flake8...
app/core/config.py:45:80: E501 line too long (85 > 79 characters)
🔍 运行 mypy...
app/models/user.py:25: error: Function is missing a return type annotation
✅ 代码检查完成
```

检查内容包括：
- **flake8**: PEP 8风格、代码复杂度、未使用变量等
- **mypy**: 类型注解检查

### 3. 安全检查

#### make security
运行安全检查：

```bash
$ make security
🔒 正在进行安全检查...
🛡️  检查代码安全性...
[main]  INFO    profile include tests: None
[main]  INFO    profile exclude tests: None
[main]  INFO    cli include tests: None
[main]  INFO    cli exclude tests: None
[main]  INFO    running on Python 3.10.6
🔍 检查依赖安全性...
Scanning dependencies...
No known security vulnerabilities found.
✅ 安全检查完成
```

检查内容包括：
- **bandit**: 代码安全漏洞检查（SQL注入、密码硬编码等）
- **safety**: 依赖包安全漏洞检查

### 4. 综合检查

#### make check
完整的代码质量检查流程：
1. 格式化代码
2. 运行lint检查

#### make check-strict
严格检查模式（不修改文件）：
1. 检查代码格式
2. 运行lint检查

#### make check-all
最全面的检查：
1. 高级代码清理
2. 代码质量检查
3. 安全检查
4. 运行测试

#### make ci-check
适用于CI/CD环境的检查：
1. 检查代码格式（不修改）
2. 代码质量检查
3. 安全检查
4. 运行测试并生成覆盖率

## 🔗 Pre-commit钩子

Pre-commit钩子会在每次git commit前自动运行代码检查，确保提交的代码质量。

### 安装
```bash
make pre-commit-install
```

### 配置
钩子配置在`.pre-commit-config.yaml`中，包括：
- 代码格式化（black, isort）
- 代码清理（autoflake, pyupgrade）
- 质量检查（flake8, mypy）
- 安全检查（bandit）
- 文件格式检查（yaml, json, toml）

### 跳过钩子
如果需要跳过某次检查：
```bash
git commit --no-verify -m "紧急修复"
```

## 📊 工具配置

### Black配置 (pyproject.toml)
```toml
[tool.black]
line-length = 120
target-version = ['py310']
exclude = '''/(migrations|alembic)/'''
```

### isort配置 (pyproject.toml)
```toml
[tool.isort]
profile = "black"
line_length = 120
multi_line_output = 3
```

### flake8配置 (.flake8)
```ini
[flake8]
max-line-length = 120
extend-ignore = E203, W503, E501
exclude = .git, __pycache__, .venv, migrations
```

### mypy配置 (mypy.ini)
```ini
[mypy]
python_version = 3.10
disallow_untyped_defs = True
ignore_missing_imports = True
```

### bandit配置 (.bandit)
```ini
[bandit]
exclude_dirs = tests, migrations, .venv
skips = B101, B601
```

## 🚀 最佳实践

### 开发工作流

1. **开发前**: 安装pre-commit钩子
   ```bash
   make pre-commit-install
   ```

2. **开发中**: 定期运行格式化
   ```bash
   make format
   ```

3. **提交前**: 运行完整检查
   ```bash
   make check
   ```

4. **发布前**: 运行全面检查
   ```bash
   make check-all
   ```

### CI/CD集成

在GitHub Actions或其他CI中使用：
```yaml
- name: 代码质量检查
  run: make ci-check
```

### IDE集成

#### VS Code
安装推荐的扩展并配置：
```json
{
  "python.formatting.provider": "black",
  "python.linting.flake8Enabled": true,
  "python.linting.mypyEnabled": true,
  "editor.formatOnSave": true
}
```

## 🔧 故障排除

### 常见问题

1. **导入排序冲突**
   - 确保isort配置为"black"配置文件
   - 运行 `make format` 自动修复

2. **mypy类型错误**
   - 添加类型注解
   - 使用 `# type: ignore` 临时忽略
   - 在mypy.ini中配置忽略规则

3. **安全检查误报**
   - 在.bandit配置中添加跳过规则
   - 使用 `# nosec` 注释忽略特定行

4. **pre-commit失败**
   - 运行 `make pre-commit-run` 查看详细错误
   - 修复问题后重新提交

### 性能优化

- 使用 `--check` 参数进行快速检查
- 在CI中缓存依赖和工具状态
- 只检查修改的文件（git diff）

这套完整的lint系统确保代码质量，提高开发效率，减少bug和安全风险。 