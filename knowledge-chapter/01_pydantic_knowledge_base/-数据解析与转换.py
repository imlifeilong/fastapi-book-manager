from pydantic import BaseModel, ConfigDict
from datetime import datetime


class User(BaseModel):
    name: str
    age: int


# 字典解析
data = {"name": "张三", "age": 20}
user = User(**data)

# 关键字参数解析
user1 = User(name="张三", age=20)

# 解析字典  model_validate () → （解析字典 / 对象）
user3 = User.model_validate({"name": "李四", "age": 30})

# 解析 ORM 对象（从数据库取数据直接转）
# user = User.model_validate(orm_user_obj)

# 前端传的 JSON 字符串直接转模型
json_str = '{"name": "王五", "age": 25}'
user4 = User.model_validate_json(json_str)

# 把规范的模型数据，转回普通字典
user_dict = user.model_dump()
# 结果: {'name': '张三', 'age': 20}

# model_dump_json () → 模型转回 JSON 字符串
json_str = user.model_dump_json(indent=2)


# 1. 字符串 → 数字
class Item(BaseModel):
    count: int
    price: float


# 字符串数字 → 自动转 int/float
item = Item(count="100", price="99.5")
print(item.count)  # 100 (int)


# 2. 字符串 → 时间（超级常用）
class Order(BaseModel):
    create_time: datetime


# 时间字符串 → 自动转 datetime 对象
order = Order(create_time="2025-01-01 12:00:00")


# 3. 任意值 → 布尔值
class Flag(BaseModel):
    open: bool


Flag(open="yes")  # True
Flag(open="no")  # False
Flag(open=1)  # True

# 1. 字段清洗（自动去空格、转小写）
from pydantic import BaseModel, field_validator


class User(BaseModel):
    email: str

    # 自动转小写 + 去空格
    @field_validator("email", mode="before")
    def clean_email(cls, value):
        return str(value).strip().lower()


# 输入: "  TEST@Example.COM  "
# 自动转换成: "test@example.com"
user = User(email="  TEST@Example.COM  ")
print(user.email)  # test@example.com


# 2. ORM 模型 → Pydantic（开发必备）
class User(BaseModel):
    name: str
    age: int

    model_config = ConfigDict(from_attributes=True)


# 直接把 ORM（如 SQLAlchemy）对象转成 Pydantic
# user = User.model_validate(orm_user)

# 完整实战流程（前端 → 后端 → 返回
# 1. 定义模型
class User(BaseModel):
    name: str
    age: int
    email: str

    @field_validator("email")
    def lower_email(cls, v):
        return v.lower()


# 2. 解析前端传来的 JSON 字符串
json_data = '{"name":"Jack","age":"28","email":"JACK@Example.com"}'
user = User.model_validate_json(json_data)

# 3. 拿到规范、安全的数据
print(user.name)  # Jack
print(user.age)  # 28 (int)
print(user.email)  # jack@example.com

# 4. 转回字典/JSON 返回给前端
# return user.model_dump()
