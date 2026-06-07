"""
Pydantic 特有类型:
数值与约束类型
    正/负数：PositiveInt, NegativeInt, PositiveFloat, NegativeFloat
    非负/正数：NonNegativeInt, NonPositiveInt, NonNegativeFloat, NonPositiveFloat
    有限浮点数：FiniteFloat (排除 inf, -inf, nan)
    自定义约束：通过 conint(), confloat(), condecimal() 等函数实现，支持 gt, lt, ge, le, multiple_of 等参数。
字符串与文本类型
    EmailStr：用于验证电子邮件地址格式，需要安装 email-validator 包 (install 'pydantic[email]')。
    NameEmail：验证并解析 "Fred Bloggs fred.bloggs@example.com" 格式的字符串，返回包含姓名和邮箱的对象。
    ImportString：将字符串形式的路径（如 math.cos）动态导入为对应的Python对象。
    Json：用于表示JSON数据，可以自动解析和序列化JSON字符串。
    ByteSize：解析带单位的字节字符串（如 1KB, 10MB），将其转换为数字。
    自定义约束：通过 constr() 函数实现，支持 min_length, max_length, pattern (正则) 等参数。

网络与资源定位类型 (URLs)
    Pydantic 内置了多种URL验证类型，简化了Web开发的校验工作：
    AnyUrl：任何URL，要求有主机名。
    AnyHttpUrl：http 或 https 协议的URL。
    HttpUrl：http 或 https 协议的URL，并要求有顶级域名，长度受限。
    FileUrl：file 协议的URL。
    数据库DSN：如 PostgresDsn, MysqlDsn 等，用于验证数据库连接字符串。
文件与路径类型
    FilePath：必须是已存在的文件路径。
    DirectoryPath：必须是已存在的目录路径。

安全与敏感信息类型
    SecretStr 和 SecretBytes：用于存储敏感信息，在打印或序列化时会自动被掩码为 '**********'，防止意外泄露。
日期时间扩展类型
    PastDate / FutureDate：必须是过去/未来的日期。
    PastDatetime / FutureDatetime：必须是过去/未来的 datetime。
    AwareDatetime / NaiveDatetime：必须是带时区/不带时区的 datetime。
"""

from pydantic import (
    BaseModel,
    EmailStr,  # 邮箱验证
    HttpUrl,  # HTTP URL
    AnyUrl,  # 任意 URL
    FilePath,  # 文件路径（必须存在）
    DirectoryPath,  # 目录路径（必须存在）
    SecretStr,  # 密码（序列化时掩码）
    SecretBytes,  # 二进制密码
    IPvAnyAddress,  # IPv4/IPv6 地址
    PaymentCardNumber,  # 信用卡号（Luhn 验证）
    ByteSize,  # 字节大小（"1GB" -> 字节数）
    PastDate,  # 过去日期
    FutureDate,  # 未来日期
    AwareDatetime,  # 带时区的时间
    NaiveDatetime,  # 不带时区的时间
)


class UserLogin(BaseModel):
    email: EmailStr
    password: SecretStr


user = UserLogin(email="user@example.com", password="my_secret_pwd")
print(user)  # password=SecretStr('**********')  ← 密码被隐藏
print(user.password.get_secret_value())  # my_secret_pwd  ← 显式获取原始值
