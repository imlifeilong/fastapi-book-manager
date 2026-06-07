# 📚 图书馆管理系统 (Library Management System)

基于 **FastAPI** + **SQLAlchemy** + **SQLite** 构建的现代化图书馆管理后端 API。

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python main.py
```

或直接使用 uvicorn：

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 访问 API 文档

启动后访问：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📋 默认账号

系统启动时会自动创建以下测试账号：

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |
| 图书管理员 | librarian | lib123 |
| 读者 | reader | reader123 |

## 🔧 API 接口概览

### 认证模块 (`/api/v1/auth`)

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| POST | `/register` | 用户注册 | 公开 |
| POST | `/login` | 用户登录 | 公开 |

### 用户管理 (`/api/v1/users`)

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | `/me` | 获取当前用户信息 | 登录用户 |
| GET | `/` | 用户列表 | admin/librarian |
| GET | `/{id}` | 用户详情 | admin/librarian |
| PUT | `/{id}` | 更新用户 | admin |
| DELETE | `/{id}` | 删除用户 | admin |

### 图书管理 (`/api/v1/books`)

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| POST | `/` | 添加图书 | admin/librarian |
| GET | `/` | 图书列表 | 登录用户 |
| GET | `/search` | 高级搜索 | 登录用户 |
| GET | `/{id}` | 图书详情 | 登录用户 |
| PUT | `/{id}` | 更新图书 | admin/librarian |
| DELETE | `/{id}` | 删除图书 | admin |

### 借阅管理 (`/api/v1/borrows`)

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| POST | `/borrow` | 借阅图书 | 登录用户 |
| POST | `/return` | 归还图书 | 登录用户/管理员 |
| POST | `/renew` | 续借图书 | 登录用户/管理员 |
| GET | `/my-borrows` | 我的借阅记录 | 登录用户 |
| GET | `/all` | 所有借阅记录 | admin/librarian |
| GET | `/statistics` | 借阅统计 | admin/librarian |
| POST | `/check-overdue` | 检查逾期 | admin/librarian |

## 🏗️ 项目结构

```
library_system/
├── main.py              # 应用入口
├── database.py          # 数据库配置
├── requirements.txt     # 依赖列表
├── models/              # 数据模型
│   ├── __init__.py
│   ├── user.py         # 用户模型
│   ├── book.py         # 图书模型
│   └── borrow.py       # 借阅记录模型
├── schemas/            # Pydantic 数据验证
│   ├── __init__.py
│   ├── user.py
│   ├── book.py
│   └── borrow.py
├── routers/            # API 路由
│   ├── __init__.py
│   ├── auth.py         # 认证路由
│   ├── users.py        # 用户路由
│   ├── books.py        # 图书路由
│   └── borrows.py      # 借阅路由
└── utils/              # 工具函数
    ├── __init__.py
    └── auth.py         # 认证工具
```

## 🔐 认证方式

使用 **JWT Bearer Token** 认证：

1. 调用 `POST /api/v1/auth/login` 获取 token
2. 在请求头中添加：`Authorization: Bearer <token>`

## ⚙️ 核心功能

- ✅ **RBAC 权限控制**：管理员、图书管理员、读者三种角色
- ✅ **图书管理**：ISBN 唯一校验、分类管理、库存管理
- ✅ **借阅流程**：借阅 → 续借（最多2次）→ 归还
- ✅ **逾期检测**：自动计算逾期天数和罚款
- ✅ **搜索功能**：支持按标题、作者、ISBN、分类搜索
- ✅ **自动文档**：Swagger UI / ReDoc 自动生成

## 📝 使用示例

### 1. 登录获取 Token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=reader&password=reader123"
```

### 2. 添加图书（管理员）

```bash
curl -X POST "http://localhost:8000/api/v1/books" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "isbn": "978-7-111-11111-1",
    "title": "Python编程从入门到实践",
    "author": "Eric Matthes",
    "publisher": "人民邮电出版社",
    "publish_year": 2020,
    "category": "计算机",
    "total_copies": 5,
    "location": "A区-3排-2层"
  }'
```

### 3. 借阅图书

```bash
curl -X POST "http://localhost:8000/api/v1/borrows/borrow" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"book_id": 1, "days": 30}'
```

### 4. 归还图书

```bash
curl -X POST "http://localhost:8000/api/v1/borrows/return" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"record_id": 1}'
```

## ⚠️ 注意事项

- 生产环境请修改 `SECRET_KEY`（位于 `utils/auth.py`）
- 默认使用 SQLite，生产环境建议切换到 PostgreSQL/MySQL
- 密码使用 bcrypt 加密存储


## 🖥️ 前端界面

项目包含一个纯前端界面，无需任何构建工具，直接打开即可使用。

### 前端文件位置
```
frontend/
├── index.html    # 主页面
├── style.css     # 样式文件
└── app.js        # 交互逻辑
```

### 启动方式

1. **启动后端服务**（确保 API 在 `http://localhost:8000` 运行）：
```bash
python main.py
```

2. **打开前端页面**：
   - 直接用浏览器打开 `frontend/index.html`
   - 或使用任意静态服务器：
```bash
cd frontend
python -m http.server 3000
# 然后访问 http://localhost:3000
```

> ⚠️ 注意：由于浏览器安全策略，直接打开 HTML 文件可能会有跨域问题。建议使用静态服务器方式，或在启动后端时添加 CORS 支持（已默认配置）。

### 前端功能

| 页面 | 功能 |
|------|------|
| **登录页** | JWT 登录、测试账号提示 |
| **数据概览** | 统计卡片、最近借阅记录 |
| **图书管理** | 搜索、筛选、分页、借阅、增删改（按权限） |
| **借阅管理** | 我的借阅 / 全部记录、归还、续借、逾期检查 |
| **用户管理** | 用户列表、添加用户（管理员） |

### 前端技术栈
- 纯 HTML5 + CSS3 + JavaScript（Vanilla JS）
- Font Awesome 图标
- 响应式布局（支持移动端）
- 无框架依赖，零构建步骤
