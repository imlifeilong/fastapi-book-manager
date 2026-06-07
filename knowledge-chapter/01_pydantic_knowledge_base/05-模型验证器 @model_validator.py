"""
@model_validator 用于需要同时访问多个字段的复杂验证，例如比较两个字段的值、依赖其他字段的默认值等。它有两种模式：'before' 和 'after'
mode='after'（默认）
    在所有字段验证完成之后运行。
    接收 self（模型实例），可以访问所有字段的已验证值。
    必须返回模型实例（通常返回 self，也可以返回新实例）。
    适用于跨字段验证、派生字段计算、整体业务规则。

mode='before'
    在字段验证之前运行。
    接收原始输入数据（通常是 dict，但也可能是任意类型）。
    必须返回用于后续验证的数据（通常是 dict）。
    适用于预处理输入（如从其他格式转换、设置默认值、清洗数据）。
"""


class Order(BaseModel):
    items: list[str]
    total: float

    @model_validator(mode="after")
    def check_total(self) -> "Order":
        if len(self.items) > 0 and self.total <= 0:
            raise ValueError("total must be positive when items exist")
        return self


# 触发验证器
try:
    Order(items=["book"], total=-5)
except ValidationError as e:
    print(e.json(indent=2))

from pydantic import BaseModel, model_validator


class Rectangle(BaseModel):
    width: float
    height: float

    @model_validator(mode='after')
    def compute_area(self) -> 'Rectangle':
        self.area = self.width * self.height  # 动态添加属性
        return self


rect = Rectangle(width=5, height=3)
print(rect.area)  # 15.0

from pydantic import BaseModel, model_validator


class Config(BaseModel):
    host: str
    port: int

    @model_validator(mode='before')
    @classmethod
    def parse_env_format(cls, data: any) -> any:
        # 如果输入是字符串 "localhost:8080"，拆分成 dict
        if isinstance(data, str):
            parts = data.split(':')
            return {'host': parts[0], 'port': int(parts[1])}
        return data


print(Config('example.com:5432'))  # host='example.com' port=5432