from pydantic import BaseModel, Field, ValidationError
from typing import Literal

"""
Pydantic 全面支持Python标准库中的常用类型:
int	                整数	        int('123') -> 123
float	            浮点数	    float('12.3') -> 12.3
str	                字符串	    str(123) -> '123'
bool	            布尔值	    bool('true') -> True, bool('false') -> False
bytes	            字节	        bytes('hello', 'utf-8')
list	            列表	        list((1, 2)) -> [1, 2]
tuple	            元组	        tuple([1, 2]) -> (1, 2)
dict	            字典      	dict([('a', 1)]) -> {'a': 1}
set	                集合      	set([1, 2]) -> {1, 2}
frozenset	        不可变集合	frozenset([1, 2])
datetime及其子类型	日期时间	    datetime.strptime('2023-01-01', '%Y-%m-%d')
Enum	            枚举	        使用Python内置的enum.Enum定义
None / NoneType	    空值	        仅允许None值



"""


class User(BaseModel):
    name: str
    age: int
    is_active: bool = True  # 默认值
    tags: list[str] = Field(default_factory=list)  # 避免可变默认值
    profile: dict[str, str] | None = None  # Python 3.10 联合类型
    level: Literal["admin", "user"] = "user"  # 字面量约束


user = User(name="Alice", age=30, tags=["a", "b"])
print(user)  # name='Alice' age=30 is_active=True tags=['a', 'b'] profile=None level='user'
print(user.model_dump())  # 转为字典
print(user.model_dump_json())  # 模型实例转为 JSON 字符串

# 2. 非法数据验证（触发异常）
try:
    User(name="李四", age="25")  # age 传入字符串，类型不匹配
except ValidationError as e:
    print("\n验证错误信息:")
    print(e.json())
