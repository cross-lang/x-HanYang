# 汉阳（HanYang）

[English](README.en.md) | 中文

## 项目简介

**汉阳（HanYang）** 是一个基于`领域驱动设计（DDD）`思想，使用 `FastAPI` 实现的生产级 Python Web 应用框架。

项目以 DDD 分层架构为核心设计思想，严格遵循领域驱动设计原则，提供完整的用户认证、RBAC 权限管理、审计日志、文件管理等企业级功能模块。适用于需要高内聚、低耦合、可扩展的中后台系统、API 网关、微服务基座等业务场景。

**核心特征：**

- 严格遵循 DDD 四层架构：领域层（Domain）→ 应用层（Application）→ 基础设施层（Infrastructure）→ 接口层（Interfaces）
- 全异步架构：基于 SQLAlchemy 2.0 异步引擎 + asyncio，适配高并发场景
- CQRS 命令/查询分离：写操作与读操作独立编排，职责清晰
- 领域事件驱动：聚合根收集领域事件，事件总线统一分发
- 工作单元（Unit of Work）：事务边界自动管理，确保数据一致性
- 生产级安全：JWT 认证、速率限制、敏感数据脱敏、生产配置校验

## 快速开始

### 1. 环境要求

| 依赖 | 版本要求 | 说明 |
|------|----------|------|
| Python | >= 3.11 | 推荐 3.11 或 3.12 |
| uv | >= 0.6 | 包管理器 |
| MySQL | >= 8.0 | 生产数据库（可选，本地开发可用 SQLite） |
| Redis | >= 7.0 | 缓存（可选） |
| Docker | >= 24.0 | 容器部署（可选） |

**操作系统适配：**

- **Windows**：安装 Python 3.11+（推荐从 [python.org](https://www.python.org/downloads/) 下载），安装 Git（[git-scm.com](https://git-scm.com/downloads)），通过 `pip install uv` 安装 uv
- **Linux**：`curl -LsSf https://astral.sh/uv/install.sh | sh` 安装 uv，Python 通过系统包管理器安装
- **macOS**：`brew install python@3.11 uv`（推荐 Homebrew），或使用官方安装器

### 2. 项目代码克隆

```bash
# 克隆仓库
git clone https://github.com/yeyushilai/x-HanYang.git

# 进入项目目录
cd x-HanYang
```

### 3. 依赖同步安装

```bash
# 安装所有依赖（基于 uv.lock 锁定文件，确保环境一致性）
uv sync

# 仅安装生产依赖（不含开发工具）
uv sync --no-dev
```

### 4. 环境配置

复制环境配置模板并按需修改：

```bash
cp .env.example .env
```

核心配置参数说明：

| 参数 | 说明 | 示例 |
|------|------|------|
| `APP_ENV` | 运行环境 | `development` / `production` |
| `APP_DEBUG` | 调试模式 | `true` / `false` |
| `DATABASE_URL` | 数据库连接 URL | `mysql+asyncmy://user:pass@localhost:3306/hanyang?charset=utf8mb4` |
| `REDIS_URL` | Redis 连接 URL | `redis://localhost:6379/0` |
| `AUTH_SECRET_KEY` | JWT 签名密钥（生产环境必须 >= 32 位随机字符串） | `your-secret-key-here` |
| `CORS_ORIGINS` | CORS 允许的来源 | `["http://localhost:3000"]` |
| `SMTP_HOST` | SMTP 邮件服务器 | `smtp.example.com` |

> 本地快速体验可使用 SQLite：`DATABASE_URL=sqlite+aiosqlite:///./data/hanyang.db`

### 5. 服务启动

**方式一：本地开发热重载（推荐）**

```bash
# 默认启动（热重载模式）
uv run x-HanYang --reload

# 自定义端口
uv run x-HanYang --reload --port 9000
```

**方式二：Docker 容器部署**

```bash
# 创建 .env 文件并配置生产环境变量
# 必须设置: AUTH_SECRET_KEY, MYSQL_PASSWORD, REDIS_PASSWORD, MYSQL_ROOT_PASSWORD

# 构建并启动全部服务（应用 + MySQL + Redis）
docker-compose up --build -d

# 查看日志
docker-compose logs -f app

# 停止服务
docker-compose down
```

**方式三：直接使用 uvicorn**

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 6. 常用工程命令

```bash
# 单元测试
uv run pytest

# 带覆盖率的测试
uv run pytest --cov=src --cov-report=html

# 代码格式化
uv run ruff format .

# 静态代码检查
uv run ruff check .

# 自动修复可修复的 lint 问题
uv run ruff check --fix .

# 类型检查
uv run mypy src

# 依赖漏洞扫描
uv run pip-audit
```

### 7. 使用方法示例

启动服务后，访问 Swagger 交互式文档：http://localhost:8000/docs

**用户登录获取令牌：**

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"account": "admin", "password": "admin12345"}'
```

**使用令牌访问受保护接口：**

```bash
# 获取当前用户信息
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <your-token>"

# 创建用户
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{"username": "newuser", "email": "new@example.com", "password": "password123"}'

# 查询用户列表
curl http://localhost:8000/api/v1/users?page=1&page_size=10 \
  -H "Authorization: Bearer <your-token>"
```

## 项目结构

```
x-HanYang/
├── alembic/                          # Alembic 数据库迁移脚本
│   ├── env.py                        # 迁移环境配置
│   ├── script.py.mako                # 迁移脚本模板
│   └── versions/                     # 迁移版本文件
├── src/
│   ├── application/                  # 应用层 — 用例编排，不含业务规则
│   │   ├── audit/                    #   审计用例（登录日志查询）
│   │   ├── auth/                     #   认证用例（登录/登出/刷新令牌）
│   │   ├── file/                     #   文件用例（上传/下载）
│   │   ├── role/                     #   角色用例（CRUD）
│   │   ├── shared/                   #   应用层共享（EventBus 抽象、UnitOfWork 抽象）
│   │   └── user/                     #   用户用例（CRUD + 搜索）
│   ├── constants/                    # 全局常量（应用元信息、认证、HTTP、分页、消息）
│   ├── domain/                       # 领域层 — 零外部依赖，纯业务逻辑
│   │   ├── audit/                    #   审计聚合（AuditLog、LoginLog）
│   │   ├── auth/                     #   认证聚合（AuthDomainService 接口、领域事件）
│   │   ├── shared/                   #   领域共享内核（Entity、ValueObject、AggregateRoot、DomainEvent、Repository 抽象）
│   │   └── user/                     #   用户聚合（User 聚合根、Role、Permission、Email/Password 值对象）
│   ├── infrastructure/               # 基础设施层 — 技术实现
│   │   ├── auth/                     #   认证服务实现（JWT + 密码哈希）
│   │   ├── config/                   #   配置管理（pydantic-settings）
│   │   ├── external/                 #   外部服务适配器（缓存、邮件、存储、HTTP 客户端、限流）
│   │   ├── messaging/                #   事件总线实现（内存事件分发器）
│   │   └── persistence/              #   持久化（异步数据库、ORM 映射、仓储实现、工作单元、迁移）
│   ├── interfaces/                   # 接口层 — HTTP / MQ / gRPC 入口
│   │   ├── http/                     #   HTTP 接口
│   │   │   ├── schemas/              #     Pydantic 请求/响应 Schema
│   │   │   └── v1/                   #     API v1 路由（health/auth/user/role/file/audit）
│   │   └── shared/                   #   接口层共享（统一响应格式）
│   ├── shared/                       # 跨层共享（日志、安全工具、框架异常）
│   ├── utils/                        # 工具函数（IP 提取、敏感数据脱敏）
│   └── main.py                       # 应用入口（工厂函数 + 生命周期管理）
├── tests/                            # 测试目录
├── scripts/                          # 运维脚本
├── .env.example                      # 环境变量模板
├── .gitignore                        # Git 忽略规则
├── alembic.ini                       # Alembic 配置
├── docker-compose.yml                # Docker Compose 编排
├── Dockerfile                        # Docker 镜像构建
├── LICENSE                           # 开源协议
├── pyproject.toml                    # 项目元信息与依赖管理
└── uv.lock                           # 依赖锁定文件
```

## 系统架构

### 分层架构

```mermaid
graph TB
    subgraph "接口层 Interfaces"
        HTTP[HTTP 路由 / 中间件 / 异常处理器]
        Schemas[Pydantic Schema 校验]
    end

    subgraph "应用层 Application"
        Commands[Command Handler]
        Queries[Query Handler]
        UoW[UnitOfWork 事务管理]
        EventBus[EventBus 事件总线]
    end

    subgraph "领域层 Domain"
        Aggregates[聚合根 / 实体 / 值对象]
        DomainEvents[领域事件]
        DomainServices[领域服务接口]
        Repositories[仓储接口]
    end

    subgraph "基础设施层 Infrastructure"
        ORM[SQLAlchemy ORM]
        Repos[仓储实现]
        JWT[JWT 认证]
        Cache[Redis 缓存]
        Email[SMTP 邮件]
        Storage[文件存储]
    end

    HTTP --> Commands
    HTTP --> Queries
    Commands --> UoW
    UoW --> Repos
    Commands --> Aggregates
    Commands --> EventBus
    Queries --> Repos
    Repos --> ORM
    Aggregates --> DomainEvents
    DomainServices --> Repositories
    Repos -.->|实现| Repositories
    JWT -.->|实现| DomainServices
```

### 用户认证流程

```mermaid
sequenceDiagram
    participant C as 客户端
    participant R as API 路由
    participant H as LoginHandler
    participant A as AuthDomainService
    participant U as UnitOfWork
    participant DB as 数据库

    C->>R: POST /api/v1/auth/login
    R->>H: handle(LoginCommand)
    H->>A: authenticate(account, password)
    A->>U: user_repo.find_by_username()
    U->>DB: SELECT
    DB-->>U: User
    A->>A: 验证密码
    A->>U: user_repo.save(record_login)
    A-->>H: TokenPair
    U->>DB: COMMIT
    H-->>R: TokenPairDTO
    R-->>C: {access_token, refresh_token}
```

### 用户创建流程

```mermaid
sequenceDiagram
    participant C as 客户端
    participant R as API 路由
    participant H as CreateUserHandler
    participant U as UnitOfWork
    participant E as EventBus
    participant DB as 数据库

    C->>R: POST /api/v1/users
    R->>H: handle(CreateUserCommand)
    H->>U: user_repo.find_by_email() 唯一性校验
    H->>H: User.create() 工厂方法创建聚合根
    H->>U: user_repo.save(user)
    H->>H: collect_and_clear_events()
    H->>E: publish_all(events)
    U->>DB: COMMIT
    H-->>R: User
    R-->>C: {id, username, email}
```

## 技术栈

| 分类 | 技术 |
|------|------|
| **开发语言** | Python 3.11+ |
| **Web 框架** | FastAPI 0.115+, Uvicorn, Gunicorn |
| **数据存储** | MySQL 8.0 (asyncmy), SQLite (aiosqlite), SQLAlchemy 2.0, Alembic |
| **缓存** | Redis 7 (redis-py async) |
| **认证** | PyJWT (JWT 令牌), bcrypt (密码哈希) |
| **配置管理** | pydantic-settings, python-dotenv |
| **日志** | Loguru |
| **限流** | slowapi |
| **HTTP 客户端** | httpx (异步, 重试) |
| **代码质量** | Ruff (格式化 + Lint), mypy (类型检查) |
| **测试** | pytest, pytest-asyncio, pytest-cov, httpx |
| **部署** | Docker, Docker Compose, uv 包管理器 |

## API 文档说明

### 交互式文档

| 文档类型 | 访问地址 | 说明 |
|----------|----------|------|
| Swagger UI | http://localhost:8000/docs | 交互式 API 文档，支持在线调试 |
| ReDoc | http://localhost:8000/redoc | 只读 API 文档，结构清晰 |
| OpenAPI JSON | http://localhost:8000/openapi.json | OpenAPI 3.0 规范文件（仅调试模式可用） |

### API 接口清单

| 模块 | 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|------|
| 健康检查 | `GET` | `/api/v1/health` | 服务健康检查 | 公开 |
| 认证 | `POST` | `/api/v1/auth/login` | 用户登录 | 公开 |
| 认证 | `POST` | `/api/v1/auth/refresh` | 刷新令牌 | 公开 |
| 认证 | `POST` | `/api/v1/auth/logout` | 退出登录 | Bearer Token |
| 认证 | `GET` | `/api/v1/auth/me` | 当前用户信息 | Bearer Token |
| 用户 | `POST` | `/api/v1/users` | 创建用户 | Bearer Token |
| 用户 | `GET` | `/api/v1/users` | 用户列表（分页） | Bearer Token |
| 用户 | `GET` | `/api/v1/users/{id}` | 查询用户详情 | Bearer Token |
| 用户 | `POST` | `/api/v1/users/{id}/update` | 更新用户 | Bearer Token |
| 用户 | `POST` | `/api/v1/users/{id}/delete` | 删除用户（软删除） | Bearer Token |
| 角色 | `POST` | `/api/v1/roles` | 创建角色 | Bearer Token |
| 角色 | `GET` | `/api/v1/roles` | 角色列表（分页） | Bearer Token |
| 角色 | `GET` | `/api/v1/roles/{id}` | 查询角色详情 | Bearer Token |
| 角色 | `POST` | `/api/v1/roles/{id}/update` | 更新角色 | Bearer Token |
| 角色 | `POST` | `/api/v1/roles/{id}/delete` | 删除角色（软删除） | Bearer Token |
| 文件 | `POST` | `/api/v1/files/upload` | 上传文件 | Bearer Token |
| 文件 | `GET` | `/api/v1/files/{key}` | 下载文件 | Bearer Token |
| 审计 | `GET` | `/api/v1/audit/login-logs` | 登录日志查询（分页） | Bearer Token |

### 权限控制

- 所有接口（除健康检查、登录、刷新令牌外）均需 Bearer Token 认证
- 令牌通过 `POST /api/v1/auth/login` 获取，有效期默认 7 天
- 支持通过 `POST /api/v1/auth/refresh` 刷新令牌

## 存储配置说明

### 数据库存储

项目使用 SQLAlchemy 2.0 异步 ORM，支持 MySQL 和 SQLite：

**MySQL（生产推荐）：**

```env
DATABASE_URL=mysql+asyncmy://用户名:密码@主机:端口/数据库名?charset=utf8mb4
```

**SQLite（本地开发）：**

```env
DATABASE_URL=sqlite+aiosqlite:///./data/hanyang.db
```

数据库迁移使用 Alembic：

```bash
# 生成迁移脚本
uv run alembic revision --autogenerate -m "描述"

# 执行迁移
uv run alembic upgrade head

# 回滚迁移
uv run alembic downgrade -1
```

### 缓存存储

```env
REDIS_URL=redis://localhost:6379/0
```

Redis 用于令牌管理、权限缓存等场景，未配置时相关功能自动降级。

### 文件存储

```env
STORAGE_PROVIDER=local          # local 或 s3
STORAGE_LOCAL_PATH=./uploads    # 本地存储路径
```

本地存储文件保存在 `STORAGE_LOCAL_PATH` 指定目录，S3 对象存储需额外安装 `boto3`：

```bash
uv pip install boto3
```

## 许可证

本项目基于 [MIT License](LICENSE) 开源。

## 参考资料

| 技术 | 官方文档 |
|------|----------|
| Python | https://docs.python.org/3/ |
| FastAPI | https://fastapi.tiangolo.com/ |
| SQLAlchemy | https://docs.sqlalchemy.org/ |
| Alembic | https://alembic.sqlalchemy.org/ |
| uv | https://docs.astral.sh/uv/ |
| Docker | https://docs.docker.com/ |
| Loguru | https://loguru.readthedocs.io/ |
| Pydantic | https://docs.pydantic.dev/ |
| Redis | https://redis.io/docs/ |
| Ruff | https://docs.astral.sh/ruff/ |
| pytest | https://docs.pytest.org/ |

## 联系方式

- **作者**：John Young（夜雨诗来）
- **邮箱**：john.young@foxmail.com
- **Gitee**：https://gitee.com/yeyushilai
- **GitHub**：https://github.com/yeyushilai
- **项目地址**：https://github.com/yeyushilai/x-HanYang
