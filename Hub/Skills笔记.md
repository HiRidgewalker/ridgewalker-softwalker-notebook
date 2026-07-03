# Skills 笔记

> 原 `文档/Skills.md` 的重新整理版本，补全了 Skills 核心特征、与 Tool/Subagent/MCP 的关系、典型结构、构建工具、资源平台。原笔记保留在原位置供回溯。

## 一、Skills 的核心定义

**Skills（技能）** 是 Anthropic 提出的 Agent 扩展机制，其关键特征是：

> **AI 会自己判断什么时候该用这个技能，主动触发，而不是你手动去点选。**

这是它和"菜单 / 按钮 / 工作流节点"最大的区别 —— Skills 是**由模型在合适的时机自动调用**的。

---

## 二、Skills 与周边概念的关系

| 概念 | 触发方式 | 适合场景 | 与 Skills 的区别 |
| --- | --- | --- | --- |
| **Tool** | LLM 在对话中按需调用 | 单次原子操作（读文件、调 API） | Tool 是细粒度能力，Skill 是一组 Tool + 指引 + 工作流的封装 |
| **Subagent** | 由主 Agent 委派子任务 | 子任务隔离、上下文分离 | Subagent 是 Agent 级拆分，Skill 是能力级封装 |
| **MCP** | LLM 通过 MCP Client 调用 MCP Server | 跨进程 / 跨服务的工具接入 | MCP 解决"工具如何接入"，Skill 解决"能力如何组织" |
| **Workflow** | 预定义流程 | 强规则、可重复 | Workflow 是显式编排，Skill 是隐式触发 |

**一句话总结**：Tool 是能力原语，MCP 是接入协议，Skill 是能力的有命名、可触发、可渐进披露的封装。

---

## 三、Skills 的典型结构

一个 Skill 通常由以下部分组成：

```
my-skill/
├── SKILL.md              # 必需：Skill 的元信息 + 使用说明
├── scripts/              # 可选：可执行脚本
├── references/           # 可选：参考文档（按需加载）
└── assets/               # 可选：模板、图片等资源
```

`SKILL.md` 顶部通常带 YAML frontmatter：

```yaml
---
name: my-skill              # 必填：Skill 名称
description: 简短描述...     # 必填：模型据此判断何时调用
---
```

> 关键设计：`description` 字段就是 Skills "主动触发"的依据 —— 模型读到这个字段后，会在合适的对话情境下自动加载并启用该 Skill。

---

## 四、构建工具

- **skill-creator**：Anthropic 官方提供的 Skills 构建工具，可以帮助你从一个想法出发，逐步生成符合规范的 Skill 包。
  - [skill-creator 仓库](https://github.com/anthropics/skills/tree/main/skills/skill-creator)
- **渐进式披露（Progressive Disclosure）**：构建 Skill 时的核心原则 —— 默认只暴露 Skill 元信息（name + description），模型决定调用时才加载详细内容，控制上下文占用。

---

## 五、资源平台

### 官方

- [Anthropic 官方构建指南](https://agentskills.io/home)
- [Anthropic Skills 官方仓库](https://github.com/anthropics/skills)
- [skill-creator 构建工具](https://github.com/anthropics/skills/tree/main/skills/skill-creator)

### 社区

- [skills.sh](https://skills.sh/)
- [awesome-claude-skills](https://github.com/composiohq/awesome-claude-skills)
- [Claude 中文社区 Skills 专区](https://claudecn.com/skills)

### 国内生态

| 资源 | 地址 | 说明 |
| --- | --- | --- |
| 扣子技能商店 | [coze.cn/skills](https://coze.cn/skills) | 国内生态最完整的 Skills 平台 |
| 小龙虾 Skills 中文官方库 | [awesome-openclaw-skills-zh](https://github.com/clawdbot-ai/awesome-openclaw-skills-zh) | 国内最重要的开源 Skills 资源库，按场景分类 |
| 腾讯 Skills Hub | [skillhub.tencent.com](https://skillhub.tencent.com) | 收录 1.3 万个 Skills，精选 Top 50 榜单 |
| Skill 导航网站 | [skillsmp.com/zh](https://skillsmp.com/zh) | Skill 聚合站，可下载压缩包一键安装到扣子 |

---

## 六、使用经验小结

- **description 写好很关键**：模型靠它判断何时触发，写得不准会"该用不用"或"乱触发"。
- **Skill 内引用保持轻量**：详细内容放 `references/`，按需加载，避免一次性占用过多上下文。
- **Skill 是组织能力，不是堆功能**：一个 Skill 应聚焦一个完整场景，而非多个无关能力的合并。
- **渐进披露是核心**：把"必要信息 / 可选细节 / 资源文件"分三层，控制上下文膨胀。