from pydantic import BaseModel, Field, ValidationError
from datetime import datetime
from uuid import uuid4

"""
default: 默认值
default_factory: 可调用对象，用于生成默认值（避免可变默认值）
    容器：list / dict / set → default_factory=list
    唯一标识：UUID、雪花 ID、自增序列
    时间：datetime.now()、utcnow()
    计算值：依赖其他字段的默认值
    随机 / 默认对象：如默认配置、空模型实例
    
alias: 字段别名
title, description: 用于文档
gt, ge, lt, le: 数值约束
min_length, max_length: 字符串/列表长度约束
pattern: 正则表达式校验
frozen: 是否禁止修改
"""


class Product(BaseModel):
    name: str = Field(
        default="匿名",  # 默认值
        min_length=2,  # 最小长度
        max_length=20,  # 最大长度
        description="用户名",  # 字段描述（用于文档）
        examples=["张三", "李四"],  # 示例值（用于文档）
        alias="username",  # 别名（赋值时可使用别名）
    )
    id: str = Field(default_factory=lambda: str(uuid4()))  # 每次生成随机的uuid
    price: float = Field(gt=0, le=10000, description="价格")
    quantity: int = Field(ge=0, description="数量")
    code: str = Field(pattern=r"^[A-Z]{2}\d{4}$")  # 正则表达式
    created_at: datetime = Field(default_factory=datetime.now)  # 每次生成当前的时间
    tags: list[str] = Field(default_factory=list)  # 每次新建空列表


try:
    p = Product(name="A", price=-5, quantity=10, code="AB1234")
except ValidationError as e:
    print(e.json(indent=2))
