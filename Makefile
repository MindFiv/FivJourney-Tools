# 旅游全程追踪系统 Makefile

.PHONY: help install dev test clean docker-build docker-run docker-stop format format-check lint check check-strict format-advanced security check-all ci-check pre-commit-install pre-commit-run pre-commit-update

# 默认目标
help:
	@echo "旅游全程追踪系统 - 开发命令"
	@echo ""
	@echo "可用命令:"
	@echo ""
	@echo "📦 依赖管理:"
	@echo "  install      - 安装项目依赖"
	@echo "  install-dev  - 安装开发依赖"
	@echo "  update       - 更新依赖"
	@echo ""
	@echo "🚀 开发命令:"
	@echo "  dev          - 启动开发服务器"
	@echo "  test         - 运行测试"
	@echo "  test-cov     - 运行测试并生成覆盖率报告"
	@echo ""
	@echo "🔧 代码质量:"
	@echo "  format         - 格式化代码 (会修改文件)"
	@echo "  format-check   - 检查代码格式 (不修改文件)"
	@echo "  format-advanced- 高级代码清理 (删除未使用导入+升级语法)"
	@echo "  lint           - 代码检查 (flake8 + mypy)"
	@echo "  security       - 安全检查 (bandit + safety)"
	@echo "  check          - 完整检查 (格式化 + 检查)"
	@echo "  check-strict   - 严格检查 (不修改文件)"
	@echo "  check-all      - 全面检查 (包括安全和测试)"
	@echo "  ci-check       - CI/CD检查 (适用于持续集成)"
	@echo ""
	@echo "🔗 Git钩子:"
	@echo "  pre-commit-install - 安装pre-commit钩子"
	@echo "  pre-commit-run     - 运行pre-commit检查"
	@echo "  pre-commit-update  - 更新pre-commit钩子"
	@echo ""
	@echo "🐳 Docker:"
	@echo "  docker-build - 构建Docker镜像"
	@echo "  docker-run   - 运行Docker容器"
	@echo "  docker-stop  - 停止Docker容器"
	@echo "  docker-logs  - 查看容器日志"
	@echo ""
	@echo "🗃️ 数据库:"
	@echo "  db-migrate   - 生成数据库迁移"
	@echo "  db-upgrade   - 应用数据库迁移"
	@echo "  db-downgrade - 回滚上一个迁移"
	@echo "  db-current   - 查看当前迁移状态"
	@echo "  db-history   - 查看迁移历史"
	@echo "  db-reset     - 重置数据库（危险操作）"
	@echo ""
	@echo "🧹 清理:"
	@echo "  clean        - 清理临时文件"

# 安装依赖
install:
	uv sync

# 安装开发依赖
install-dev:
	uv sync --extra dev

# 启动开发服务器
dev:
	uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 运行测试
test:
	uv run pytest tests/ -v

# 测试覆盖率
test-cov:
	uv run pytest tests/ -v --cov=app --cov-report=html

# 格式化代码
format:
	@echo "🔧 正在格式化代码..."
	uv run black app/ main.py tests/ --line-length 79
	uv run isort app/ main.py tests/
	@echo "✅ 代码格式化完成"

# 检查代码格式 (不修改文件)
format-check:
	@echo "🔍 检查代码格式..."
	uv run black app/ main.py tests/ --check --line-length 79
	uv run isort app/ main.py tests/ --check-only
	@echo "✅ 代码格式检查完成"

# 代码检查
lint:
	@echo "🔍 正在进行代码检查..."
	@echo "📋 运行 flake8..."
	uv run flake8 app/ main.py tests/
	@echo "🔍 运行 mypy..."
	uv run mypy app/ main.py tests/
	@echo "✅ 代码检查完成"

# 完整的代码质量检查 (格式化 + 检查)
check:
	@echo "🚀 开始完整代码质量检查..."
	$(MAKE) format
	$(MAKE) lint
	@echo "✅ 所有检查完成"

# 严格的代码质量检查 (不修改文件)
check-strict:
	@echo "🚀 开始严格代码质量检查..."
	$(MAKE) format-check
	$(MAKE) lint
	@echo "✅ 严格检查完成"

# 高级代码清理和优化
format-advanced:
	@echo "🔧 正在进行高级代码清理..."
	@echo "🗑️  删除未使用的导入..."
	uv run autoflake --remove-all-unused-imports --recursive --in-place app/ main.py tests/
	@echo "⬆️  升级Python语法..."
	find app/ tests/ -name "*.py" -exec uv run pyupgrade --py310-plus {} \; || true
	uv run pyupgrade --py310-plus main.py || true
	@echo "🔧 格式化代码..."
	$(MAKE) format
	@echo "✅ 高级代码清理完成"

# 安全检查
security:
	@echo "🔒 正在进行安全检查..."
	@echo "🛡️  检查代码安全性..."
	uv run bandit -r app/ main.py -f json -o bandit-report.json || uv run bandit -r app/ main.py
	@echo "🔍 检查依赖安全性..."
	uv run safety check || echo "⚠️  发现安全问题，请检查上述输出"
	@echo "✅ 安全检查完成"

# 完整的代码质量检查 (包括安全)
check-all:
	@echo "🚀 开始完整代码质量检查..."
	$(MAKE) format-advanced
	$(MAKE) lint
	$(MAKE) security
	$(MAKE) test
	@echo "🎉 所有检查完成！代码质量良好"

# CI/CD 检查 (适用于持续集成)
ci-check:
	@echo "🤖 CI/CD 检查开始..."
	$(MAKE) format-check
	$(MAKE) lint
	$(MAKE) security
	$(MAKE) test-cov
	@echo "✅ CI/CD 检查完成"

# Pre-commit 相关命令
pre-commit-install:
	@echo "🔗 安装pre-commit钩子..."
	uv run pre-commit install
	@echo "✅ Pre-commit钩子安装完成"

pre-commit-run:
	@echo "🔍 运行pre-commit检查..."
	uv run pre-commit run --all-files
	@echo "✅ Pre-commit检查完成"

pre-commit-update:
	@echo "⬆️  更新pre-commit钩子..."
	uv run pre-commit autoupdate
	@echo "✅ Pre-commit钩子更新完成"

# 更新依赖
update:
	uv lock --upgrade

# 清理临时文件
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -f *.db

# Docker相关命令
docker-build:
	docker build -t travel-tracker .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

docker-logs:
	docker-compose logs -f app

# 数据库迁移（如果使用Alembic）
db-init:
	uv run alembic init alembic

db-migrate:
	uv run alembic revision --autogenerate -m "Migration"

db-upgrade:
	uv run alembic upgrade head

db-downgrade:
	uv run alembic downgrade -1

db-current:
	uv run alembic current

db-history:
	uv run alembic history

db-reset:
	@echo "⚠️  警告：这将删除所有数据！"
	@read -p "确定要重置数据库吗？(y/N): " confirm && [ "$$confirm" = "y" ]
	/opt/homebrew/opt/postgresql@16/bin/dropdb fivjourney_tools --if-exists
	/opt/homebrew/opt/postgresql@16/bin/createdb fivjourney_tools
	uv run alembic upgrade head

# 生产部署
deploy-prod:
	docker-compose -f docker-compose.prod.yml up -d 