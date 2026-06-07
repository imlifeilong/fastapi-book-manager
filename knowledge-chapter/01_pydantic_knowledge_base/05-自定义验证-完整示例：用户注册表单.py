from pydantic import BaseModel, EmailStr, Field, ValidationError, field_validator, model_validator
from typing import Optional


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    confirm_password: str
    age: Optional[int] = None
    referral_code: Optional[str] = None

    # 字段级：密码不能包含邮箱前缀
    @field_validator('password')
    @classmethod
    def password_not_contain_email_local(cls, v: str, info):
        email = info.data.get('email')
        if email and email.split('@')[0] in v:
            raise ValueError('password should not contain email local part')
        return v

    # 字段级：年龄必须大于0（如果提供）
    @field_validator('age', mode='after')
    @classmethod
    def check_age_positive(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError('age must be positive')
        return v

    # 模型级：密码和确认密码一致
    @model_validator(mode='after')
    def passwords_match(self) -> 'UserRegister':
        if self.password != self.confirm_password:
            raise ValueError('password and confirm_password do not match')
        return self

    # 模型级：如果是通过推荐码注册，年龄必须>=18
    @model_validator(mode='after')
    def age_requirement_for_referral(self) -> 'UserRegister':
        if self.referral_code and self.age is not None and self.age < 18:
            raise ValueError('Referral users must be at least 18 years old')
        return self


# 测试
try:
    user = UserRegister(
        email='alice@example.com',
        password='alice123456',  # 包含邮箱本地部分 'alice' -> 错误
        confirm_password='alice123456',
        age=25
    )
except ValidationError as e:
    print(e)
