# Vue3 前端工程化版本

基于 **Vue 3 + Vite + Element Plus + Pinia + Vue Router** 构建的现代化前端。

## 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue 3 | ^3.4 | 前端框架 |
| Vite | ^5.2 | 构建工具 |
| Element Plus | ^2.6 | UI 组件库 |
| Pinia | ^2.1 | 状态管理 |
| Vue Router | ^4.3 | 路由管理 |
| Axios | ^1.6 | HTTP 请求 |
| Dayjs | ^1.11 | 日期处理 |
| NProgress | ^0.2 | 进度条 |

## 项目结构

```
frontend-vue3/
├── public/                 # 静态资源
├── src/
│   ├── api/               # API 接口封装
│   │   ├── auth.js
│   │   ├── book.js
│   │   ├── borrow.js
│   │   └── user.js
│   ├── assets/
│   │   └── styles/
│   │       └── main.scss  # 全局样式
│   ├── components/        # 公共组件
│   ├── layouts/
│   │   └── MainLayout.vue # 主布局
│   ├── router/
│   │   └── index.js       # 路由配置
│   ├── stores/
│   │   └── user.js        # 用户状态
│   ├── utils/
│   │   ├── request.js     # Axios 封装
│   │   └── format.js      # 格式化工具
│   ├── views/
│   │   ├── login/         # 登录页
│   │   ├── dashboard/     # 数据概览
│   │   ├── books/         # 图书管理
│   │   ├── borrows/       # 借阅管理
│   │   └── users/         # 用户管理
│   ├── App.vue
│   └── main.js            # 入口
├── index.html
├── package.json
├── vite.config.js
└── README.md
```

## 快速开始

### 1. 安装依赖

```bash
cd frontend-vue3
npm install
# 或
yarn install
```

### 2. 开发模式

```bash
npm run dev
```

> 默认端口 3000，会自动代理 `/api` 到 `http://localhost:8000`

### 3. 生产构建

```bash
npm run build
```

构建产物在 `dist/` 目录。

## 核心特性

- ✅ **Vite 极速构建** - 秒级冷启动，毫秒级热更新
- ✅ **Element Plus 组件库** - 丰富的 UI 组件，暗色模式支持
- ✅ **Pinia 状态管理** - 类型安全，DevTools 友好
- ✅ **Vue Router 路由守卫** - 权限控制，页面过渡动画
- ✅ **Axios 请求封装** - 统一拦截，错误处理，自动 Token
- ✅ **响应式布局** - 适配桌面/平板/手机
- ✅ **NProgress 进度条** - 路由切换加载提示
- ✅ **SCSS 预处理器** - 变量、嵌套、混合
