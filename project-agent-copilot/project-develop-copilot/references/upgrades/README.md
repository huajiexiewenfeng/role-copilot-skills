# Project Develop Copilot Upgrade Notes

本目录用于保存 Project Develop Copilot 的重要升级说明和技术复盘。

它记录一次升级为什么发生、采用了哪些架构决策、如何验证，以及仍然存在什么边界。普通功能需求、Bug Brief、临时工作上下文和执行计划不放在这里。

## 命名规范

```text
YYYY-MM-DD-<scope>-upgrade-retrospective.<language>.md
```

例如：

```text
2026-07-25-project-develop-copilot-upgrade-retrospective.zh.md
```

## 内容要求

每份升级说明至少包含：

- 升级日期和对应提交；
- 改造背景与原始问题；
- 根因和关键技术决策；
- 实施阶段与主要变更；
- 验证方法和结果；
- 用户与开发者影响；
- 已知局限和残余风险；
- 后续验证或演进建议。

只记录已经发生且有证据支持的结果。未完成的模型认证、外部验证或后续计划必须明确标记，不能写成已经完成。

## 文档索引

| 日期 | 范围 | 文档 | 说明 |
|---|---|---|---|
| 2026-07-25 | Project Develop Copilot | [改造升级技术复盘](./2026-07-25-project-develop-copilot-upgrade-retrospective.zh.md) | 初始化 Gate、Blackbox Eval、Mechanical Artifact、Project Graph Viewer 与顶级模型适配 |
