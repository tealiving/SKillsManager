---
name: python-enterprise-development
description: Use when implementing or refactoring Python behavior that needs enterprise layered architecture, Chinese reST docstring/comment standards, and performance-conscious concurrency design (thread/process/async).
---

# Python 企业级开发规范

## 核心原则
- 先架构、后实现，先验证、后宣称完成。
- 分层清晰、依赖单向、接口稳定。
- 中文文档可读且可执行，性能设计前置而非事后补救。

## 强制输出（编码前）
每次功能/行为改动，先给出 `Architecture Brief`：
1. 分层归属：Presentation / Application / Domain / Infrastructure
2. 依赖方向：新增依赖是否跨层穿透
3. 数据契约：DTO/接口/事件是否变化
4. 异常策略：错误分类、传播、兜底和用户可见信息
5. 测试策略：单元/集成/回归覆盖范围
6. 性能策略：瓶颈假设、并发模型、验证指标

## 分层与拆分规则
- 控制器/UI 层只做交互编排，不承载业务规则。
- 业务编排放 Application，用例通过端口调用基础设施。
- Domain 保持框架无关，不直接依赖 UI、数据库驱动、HTTP 框架。
- 文件同时出现“UI逻辑 + 业务编排 + IO细节”时必须拆分。
- 单文件超过 500 行时，默认评估并执行拆分（除生成代码或明确例外）。

## 中文注释与 Docstring 规则
- 所有函数（含私有函数）必须有中文为主的 reST docstring。
- docstring 必须包含 `:param`，并在有返回值时包含 `:return:`；无返回值写 `:return: None`。
- 注释仅用于复杂/易误解处，强调意图、约束、原因，不复述显然实现。
- 保留既有英文注释，除非用户明确要求翻译。

## 并发与性能选型矩阵
- CPU 密集：优先 `multiprocessing` / `ProcessPoolExecutor`。
- IO 密集：优先 `asyncio`；同步栈下使用有上限的 `ThreadPoolExecutor`。
- GUI 场景：主线程只负责渲染与交互；耗时任务使用工作线程（Qt 场景用 `QThread` + signal）。
- 所有并发方案都要明确：
  - 最大并发度（避免资源打爆）
  - 超时策略
  - 取消机制
  - 失败重试/降级策略

## 性能验证要求
- 变更前定义指标：延迟、吞吐、内存、CPU 至少一个主指标。
- 变更后提供对比证据（基线 vs 变更后）。
- 无法测量时给出原因与替代证据（采样日志、profile 片段、压测样本）。

## 完成前检查
- [ ] Architecture Brief 已提供且与实现一致
- [ ] 无跨层违规依赖
- [ ] 函数 docstring/中文注释满足规范
- [ ] 行为变更已有测试覆盖
- [ ] 性能敏感改动有量化验证
