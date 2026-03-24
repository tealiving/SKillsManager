---
name: enterprise-layered-architecture
description: Use when implementing features, refactors, or behavior changes that require explicit layered architecture boundaries, dependency direction control, and architecture-first design outputs before coding.
---

# Enterprise Layered Architecture

## Core Rule
先架构、后实现。任何功能改动先提交 `Architecture Brief`。

## Required Output
在写代码前，先输出以下 5 项：
1. 分层归属：Presentation / Application / Domain / Infrastructure
2. 依赖方向：谁依赖谁，是否存在跨层穿透
3. 数据契约：DTO/接口/模型是否变化
4. 异常策略：错误分类、传播与兜底
5. 测试策略：新增单测与必要集成测试

## Dependency Matrix
- Allowed: Presentation -> Application -> Domain
- Allowed: Infrastructure -> (implements ports used by upper layers)
- Forbidden: Domain -> UI/DB/HTTP framework
- Forbidden: Presentation -> Infrastructure (except composition root wiring)

## Implementation Guidance
- 领域规则放在 Domain，不放 UI/Controller。
- 外部系统访问通过 Port/Adapter 隔离。
- 优先做小步可回滚修改，避免大爆改。

## Completion Checklist
- [ ] 已提供 Architecture Brief
- [ ] 无跨层违规依赖
- [ ] 测试覆盖新增/变更行为
- [ ] 变更说明包含架构取舍