---
name: architecture-review-checklist
description: Use when preparing code review, finishing implementation, or validating whether a change meets enterprise layered architecture standards and maintainability requirements.
---

# Architecture Review Checklist

## Goal
在提交前，快速判断是否满足企业级分层与可维护性标准。

## Review Items
1. 分层边界
   - 业务规则是否混入 UI/Controller？
   - Domain 是否依赖框架或基础设施细节？
2. 依赖方向
   - 是否出现跨层反向依赖？
   - 是否通过接口隔离 Infra 细节？
3. 契约一致性
   - DTO/接口变更是否同步调用方与文档？
4. 错误处理
   - 异常是否分层处理并可观测？
5. 可测试性
   - 新行为是否有测试？
   - 关键路径是否可独立验证？

## Risk Rating
- Low: 仅局部改动、边界清晰、测试完备
- Medium: 有局部耦合但可控
- High: 跨层耦合明显、测试缺失、不可回滚

## Output Format
- Findings:
- Risk Level:
- Required Fixes:
- Nice-to-have Improvements: