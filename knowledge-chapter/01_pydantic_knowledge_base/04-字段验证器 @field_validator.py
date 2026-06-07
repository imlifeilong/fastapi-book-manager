from pydantic import BaseModel, field_validator, model_validator, ValidationError

"""
@field_validator 用于对一个或多个字段的值进行自定义验证。它可以在 Pydantic 内置类型验证之后（或之前，取决于 mode）运行。
    field_name：验证器所作用的字段名（字符串）。
    check_fields：默认 True，如果设为 False，即使字段不在模型中也不会报错（用于继承场景）。
    mode：'after'（默认）	内置类型转换和验证之后	已经是目标类型（如 int、str）
          'before'	内置验证之前	原始输入值（可能是任意类型，如 JSON 的 Any）
"""


class Person(BaseModel):
    name: str
    age: int

    # 验证单个字段
    @field_validator("name")
    @classmethod
    def name_must_be_titlecase(cls, v: str) -> str:
        if not v.istitle():
            raise ValueError("name must be title case")
        return v

    # 验证多个字段（同时验证 age 和 name）
    @field_validator('age', 'name')
    @classmethod
    def check_age_and_name(cls, v, info):
        # info.data 可以访问其他字段的当前值
        if info.field_name == 'age' and v < 0:
            raise ValueError('age must be positive')
        return v

    @field_validator("age", mode="before")
    @classmethod
    def parse_age(cls, v: str | int) -> int:
        # 在验证之前将字符串转为整数
        if isinstance(v, str):
            return int(v)
        return v


# 测试
try:
    user = Person(name='  alice  ', age=25)
    print(user)  # name='Alice' age=25  (空格被去除并首字母大写)
except ValidationError as e:
    print(e)

# age 字符串自动转换
p = Person(name="Alice", age="30")
print(p.age)  # 30

from pydantic import BaseModel, field_validator


class Demo(BaseModel):
    value: int

    @field_validator('value', mode='before')
    @classmethod
    def parse_string_to_int(cls, v):
        # 输入可能是字符串 "123"，Pydantic 还没处理
        if isinstance(v, str) and v.startswith('num:'):
            return int(v[4:])
        return v

    @field_validator('value', mode='after')
    @classmethod
    def check_positive(cls, v: int):
        if v <= 0:
            raise ValueError('value must be positive')
        return v


print(Demo(value='num:42'))  # value=42
