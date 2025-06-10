from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("密码至少需要6个字符")
        return v


class UserLogin(BaseModel):
    username: str
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if v is not None:
            # 去掉空格和特殊字符，只保留数字
            clean_phone = "".join(c for c in v if c.isdigit())
            if len(clean_phone) > 20:  # 限制长度
                raise ValueError("电话号码长度不能超过20位")
            if len(clean_phone) > 0 and len(clean_phone) < 10:  # 最少10位
                raise ValueError("电话号码至少需要10位数字")
        return v


class UserResponse(UserBase):
    id: int
    avatar: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
