from pydantic import BaseModel, ConfigDict, ValidationError

"""
配置项	                类型	    默认值	说明
extra	                str	    ignore	额外字段处理：forbid（禁止）/allow（允许）/ignore（忽略）Pydantic
strict	                bool	False	严格模式：类型不匹配直接报错，不自动转换Pydantic
from_attributes	        bool	False	从 ORM 对象创建模型（原 orm_mode）Pydantic
validate_assignment	    bool	False	赋值时是否重新验证字段
frozen	                bool	False	模型实例不可变（类似冻结 dataclass）
str_to_lower	        bool	False	字符串自动转小写Pydantic
str_max_length	        int	    None	字符串最大长度
coerce_numbers_to_str	bool	False	数字自动转为字符串Pydantic
json_schema_extra	    dict	None	自定义 JSON Schema 额外信息
"""


# 掉钱版第三大区-掉钱一区网通
class StrictUser(BaseModel):
    model_config = ConfigDict(
        extra="forbid",  # 禁止额外字段
        str_strip_whitespace=True,  # 去除字符串前后空格
        validate_assignment=True,  # 赋值时验证
        frozen=True,  # 实例不可变
    )
    name: str
    age: int


# 尝试传入额外字段（会报错）
try:
    su = StrictUser(name="  Bob  ", age=25, extra_field="not allowed")
except ValidationError as e:
    print(e.json(indent=2))

# 正常创建，名字空格被去除
su = StrictUser(name="  Bob  ", age=25)
print(su.name)  # "Bob"

# 尝试修改属性（会报错，因为 frozen=True）
# su.name = "Charlie"  # ValidationError
