# x-HanYang

基于 **DDD（Domain-Driven Design）** 架构的 FastAPI 生产级 Python Web 应用框架。

## 架构分层

```
src/
├── domain/            # 领域层 — 零外部依赖，纯业务逻辑
│   ├── shared/        #   领域共享内核（基类、值对象、事件）
│   ├── user/          #   用户聚合（聚合根 + 实体 + 值对象 + 仓储接口）
│   ├── auth/          #   认证聚合
│   └── audit/         #   审计聚合
├── application/       # 应用层 — 用例编排，不含业务规则
│   ├── user/          #   用户用例（Command / Query / DTO）
│   ├── auth/          #   认证用例
│   └── shared/        #   应用层共享（接口、事件总线抽象）
├── infrastructure/    # 基础设施层 — 技术实现
│   ├── persistence/   #   ORM 映射、仓储实现、数据库迁移
│   ├── messaging/     #   事件总线实现
│   ├── external/      #   外部服务适配器（邮件、缓存、存储）
│   └── config/        #   配置加载
├── interfaces/        # 接口层 — HTTP / MQ / gRPC 入口
│   ├── http/          #   FastAPI 路由、中间件、DI
│   └── shared/        #   接口层共享（响应格式、分页）
├── shared/            # 跨层共享（配置、异常、日志、安全）
└── main.py            # 应用入口
```

## 依赖方向

```
interfaces → application → domain ← infrastructure
```

- **domain 层零依赖**：不依赖任何框架
- **infrastructure 实现 domain 接口**：仓储、事件总线
- **application 编排领域对象**：只做流程协调
- **interfaces 转发到 application**：路由 → Command/Query Handler

## 快速开始

```bash
# 安装依赖
uv sync

# 启动服务
uv run x-HanYang

# 开发模式（热重载）
uv run x-HanYang --reload
```

## License

MIT
