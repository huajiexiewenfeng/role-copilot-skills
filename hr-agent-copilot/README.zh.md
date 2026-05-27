# HR Agent Copilot

面向简历筛选、候选人明细报告和面试题生成的角色型 Agent Copilot。

[English](./README.md) | 简体中文

## 这是什么？

HR Agent Copilot 是 Role Copilot Skills 里的 HR 招聘角色组。

它帮助 HR、招聘负责人和技术面试官，把招聘筛选流程沉淀成可复用的 AI 辅助 skills。当前 skills 来自之前的 `hr-recruiting-screening-skill` 项目，并按照 Agent Copilot 角色目录重新组织。

## 当前 Skills

| Skill | 使用场景 |
|---|---|
| `hr-resume-screening-copilot` | 第一轮筛选：根据 JD 对简历进行匹配、排序、100 分制评分，并推荐面试候选人。 |
| `hr-candidate-detail-report-copilot` | 解释候选人的得分原因、优势、短板、风险点、学历/公司/稳定度信号和面试验证点。 |
| `hr-interview-question-generator-copilot` | 为候选人生成定制化面试重点、面试题、参考答案要点、追问和弱回答信号。 |

## 共享资源

```text
hr-agent-copilot/
  references/
    scoring-rubric.md
    report-template.md
    interview-template.md
  scripts/
    extract_resumes.py
    requirements.txt
  examples/
    sample-jd.md
    sample-output.md
```

## 安装

安装单个 skill：

```bash
npx skills add huajiexiewenfeng/role-copilot-skills/hr-agent-copilot/hr-resume-screening-copilot
```

逐个安装全部 HR skills：

```bash
npx skills add huajiexiewenfeng/role-copilot-skills/hr-agent-copilot/hr-resume-screening-copilot
npx skills add huajiexiewenfeng/role-copilot-skills/hr-agent-copilot/hr-candidate-detail-report-copilot
npx skills add huajiexiewenfeng/role-copilot-skills/hr-agent-copilot/hr-interview-question-generator-copilot
```

## 典型流程

```text
JD + 简历
-> hr-resume-screening-copilot
-> hr-candidate-detail-report-copilot
-> hr-interview-question-generator-copilot
-> 面试计划和验证重点
```

## PDF 简历抽取

如果简历是 PDF，且还没有抽取文本，可以使用：

```bash
python scripts/extract_resumes.py --input "D:/resumes/backend" --output output/hr-resume-extracts
```

## 安全和判断边界

- 不替代最终招聘决策。
- 区分简历事实和分析判断。
- 模糊经历应作为面试验证点，而不是直接否决。
- 不根据受保护身份特征做歧视性判断。
- 年龄只在用户明确要求时，作为职业阶段或岗位层级匹配的辅助信息讨论。

