# 重新导出security模块中的认证函数以保持API一致性
from app.core.security import get_current_active_user, get_current_user

__all__ = ["get_current_user", "get_current_active_user"]
