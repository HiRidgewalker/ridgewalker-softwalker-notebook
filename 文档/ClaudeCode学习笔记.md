## Claude Code是如何工作的
Claude Code 是一个在您的终端中运行的代理助手。虽然它在编码方面表现出色，但它可以帮助您完成从命令行可以做的任何事情：编写文档、运行构建、搜索文件、研究主题等。

### /sandbox相关
1. Claude Code 默认开启了 sandbox 吗？
	>没有。 Claude Code 默认运行在基于权限的模式（permission-based model）下，默认是只读的，在进行修改或运行命令之前会询问权限。 [Anthropic](https://www.anthropic.com/engineering/claude-code-sandboxing) Sandbox 是一个需要主动开启的功能。需要在会话中输入 `/sandbox` 命令来启用它。 [GitHub](https://github.com/trailofbits/claude-code-config)

2. 开启 auto-allow 模式后，默认授予写权限的是当前工作目录吗？
	>是的。 在文件系统层面，写入权限默认限定在当前工作目录及其子目录；读取权限则覆盖整个系统（除了你明确拒绝的目录）。 [Claude Fast](https://claudefa.st/blog/guide/sandboxing-guide) 在 auto-allow 模式下，bash 命令会尝试在 sandbox 内运行并自动被允许，无需逐条询问权限；但对于无法在 sandbox 内执行的命令（例如需要访问未允许的网络主机），则会回退到常规的权限流程。 [Claude](https://code.claude.com/docs/en/sandboxing)

3. 如果 agent 需要安装全局 Python 第三方包（sandbox 无法执行），会询问权限并在 sandbox 外执行吗？
	>会的，这正是设计好的"逃生通道"机制。 Claude Code 内置了一个有意为之的逃生通道（escape hatch）机制，允许命令在必要时在 sandbox 外运行。当命令因 sandbox 限制失败时（例如网络连接问题或不兼容的工具），Claude 会被提示分析失败原因，并可能使用 `dangerouslyDisableSandbox` 参数重试该命令。 [Claude](https://code.claude.com/docs/en/sandboxing)

安装全局包（如 `pip install -g` 或 `pip install --user` 到 sandbox 工作目录之外）因为需要写入 sandbox 边界之外的路径，属于这种情况。Claude 会识别失败、分析原因，然后请求在 sandbox 外执行，用户会看到权限提示并可以选择是否允许。

### 代理循环
当您给 Claude 一个任务时，它会经历三个阶段：**收集上下文**、**采取行动**和**验证结果**。这些阶段相互融合。Claude 始终使用工具，无论是搜索文件以了解您的代码、编辑以进行更改，还是运行测试以检查其工作。
![[Pasted image 20260314184846.png]]
循环会根据您的要求进行调整。关于您代码库的问题可能只需要收集上下文。错误修复会循环通过所有三个阶段多次。重构可能涉及广泛的验证。Claude 根据从前一步学到的内容决定每一步需要什么，将数十个操作链接在一起并沿途进行纠正。

您也是这个循环的一部分。您可以在任何时刻中断以引导 Claude 朝不同方向发展、提供额外上下文或要求它尝试不同的方法。Claude 自主工作但对您的输入保持响应。

代理循环由两个组件驱动：[推理的模型](https://code.claude.com/docs/zh-CN/how-claude-code-works#models)和[采取行动的工具](https://code.claude.com/docs/zh-CN/how-claude-code-works#tools)。Claude Code 充当围绕 Claude 的**代理工具**：它提供工具、上下文管理和执行环境，将语言模型转变为能够进行编码的代理。

#### 模型
Claude Code 使用 Claude 模型来理解您的代码并推理任务。Claude 可以读取任何语言的代码、理解组件如何连接，以及找出需要改变什么来实现您的目标。对于复杂任务，它将工作分解为步骤、执行它们，并根据学到的内容进行调整。

[多个模型](https://code.claude.com/docs/zh-CN/model-config)可用，具有不同的权衡。Sonnet 可以很好地处理大多数编码任务。Opus 为复杂的架构决策提供更强的推理能力。在会话期间使用 `/model` 切换或使用 `claude --model <name>` 启动。

当本指南说”Claude 选择”或”Claude 决定”时，是模型在进行推理。

#### 工具
工具是使 Claude Code 成为代理的原因。没有工具，Claude 只能用文本回应。有了工具，Claude 可以采取行动：读取您的代码、编辑文件、运行命令、搜索网络并与外部服务交互。每个工具使用都会返回信息，反馈到循环中，告知 Claude 的下一个决定。内置工具通常分为五类，每一类代表不同类型的代理能力。

|类别|Claude 可以做什么|
|---|---|
|**文件操作**|读取文件、编辑代码、创建新文件、重命名和重新组织|
|**搜索**|按模式查找文件、使用正则表达式搜索内容、探索代码库|
|**执行**|运行 shell 命令、启动服务器、运行测试、使用 git|
|**网络**|搜索网络、获取文档、查找错误消息|
|**代码智能**|编辑后查看类型错误和警告、跳转到定义、查找引用（需要[代码智能插件](https://code.claude.com/docs/zh-CN/discover-plugins#code-intelligence)）|

这些是主要功能。Claude 还有用于生成 subagents、询问您问题和其他编排任务的工具。有关完整列表，请参阅[Claude 可用的工具](https://code.claude.com/docs/zh-CN/settings#tools-available-to-claude)。Claude 根据您的提示和沿途学到的内容选择使用哪些工具。当您说”修复失败的测试”时，Claude 可能会：

1. 运行测试套件以查看失败的内容
2. 读取错误输出
3. 搜索相关源文件
4. 读取这些文件以理解代码
5. 编辑文件以修复问题
6. 再次运行测试以验证

每个工具使用都给 Claude 新信息，告知下一步。这就是代理循环的实际应用。**扩展基本功能：** 内置工具是基础。您可以使用 [skills](https://code.claude.com/docs/zh-CN/skills) 扩展 Claude 知道的内容、使用 [MCP](https://code.claude.com/docs/zh-CN/mcp) 连接到外部服务、使用 [hooks](https://code.claude.com/docs/zh-CN/hooks) 自动化工作流，以及使用 [subagents](https://code.claude.com/docs/zh-CN/sub-agents) 卸载任务。这些扩展形成了核心代理循环之上的一层。有关为您的需求选择正确扩展的指导，请参阅[扩展 Claude Code](https://code.claude.com/docs/zh-CN/features-overview)。


[claude code是如何工作的以及使用建议](https://code.claude.com/docs/zh-CN/how-claude-code-works)

## 扩展Claude Code
### claude.md vs skills vs rules

![[Pasted image 20260314235621.png]]
claude.md始终是加载到上下文的，而skills是按需加载的

### 组合功能
每个扩展解决不同的问题：CLAUDE.md 处理始终开启的上下文，skills 处理按需知识和工作流，MCP 处理外部连接，subagents 处理隔离，hooks 处理自动化。真实的设置根据您的工作流组合它们。
![[Pasted image 20260314235955.png]]

### 了解claude code各个功能的上下文成本
您添加的每个功能都会消耗 Claude 的一些上下文。太多可能会填满您的上下文窗口，但它也可能增加噪音，使 Claude 效率降低；skills 可能无法正确触发，或 Claude 可能会失去对您的约定的跟踪。了解这些权衡有助于您构建有效的设置。

**`每个功能都有不同的加载策略和上下文成本`**
![[Pasted image 20260315000246.png]]

### 了解功能如何加载
[官方链接](https://code.claude.com/docs/zh-CN/features-overview#了解功能如何加载)
![[Pasted image 20260315000508.png]]

CLAUDE.md文件的位置
![[Pasted image 20260315001138.png]]
简单总结：
项目级别： `./.claude/CLAUDE.md`
用户级别： `~/.claude/CLAUDE.md`

项目 CLAUDE.md 可以存储在 `./CLAUDE.md` 或 `./.claude/CLAUDE.md` 中。创建此文件并添加适用于在项目上工作的任何人的指令：构建和测试命令、编码标准、架构决策、命名约定和常见工作流。这些指令通过版本控制与您的团队共享，因此请关注项目级标准而不是个人偏好。

运行 `/init` 自动生成起始 CLAUDE.md。Claude 分析您的代码库并创建一个包含构建命令、测试指令和它发现的项目约定的文件。如果 CLAUDE.md 已存在，`/init` 会建议改进而不是覆盖它。从那里进行细化，添加 Claude 不会自己发现的指令。

CLAUDE.md文件中倒入其他文件
CLAUDE.md 文件可以使用 `@path/to/import` 语法导入其他文件。导入的文件在启动时展开并加载到上下文中，与引用它们的 CLAUDE.md 一起。允许相对路径和绝对路径。相对路径相对于包含导入的文件解析，而不是工作目录。导入的文件可以递归导入其他文件，最大深度为五跳。要引入 README、package.json 和工作流指南，请在 CLAUDE.md 中的任何位置使用 `@` 语法引用它们：
```md

有关项目概述，请参阅 @README，有关此项目的可用 npm 命令，请参阅 @package.json。

# 其他指令
- git 工作流 @docs/git-instructions.md
```

claude code rules
对于较大的项目，您可以使用 `.claude/rules/` 目录将指令组织到多个文件中。这使指令保持模块化并更容易让团队维护。规则也可以 [范围限定为特定文件路径](https://code.claude.com/docs/zh-CN/memory#path-specific-rules)，因此它们仅在 Claude 处理匹配文件时加载到上下文中，减少噪音并节省上下文空间。

在项目的 `.claude/rules/` 目录中放置 markdown 文件。每个文件应涵盖一个主题，具有描述性文件名，如 `testing.md` 或 `api-design.md`。所有 `.md` 文件都被递归发现，因此您可以将规则组织到子目录中，如 `frontend/` 或 `backend/`：

![[Pasted image 20260315002638.png]]

没有 [`paths` frontmatter](https://code.claude.com/docs/zh-CN/memory#path-specific-rules) 的规则在启动时加载，优先级与 `.claude/CLAUDE.md` 相同。

#### 特定路径的规则

规则可以使用带有 `paths` 字段的 YAML frontmatter 范围限定为特定文件。这些条件规则仅在 Claude 处理与指定模式匹配的文件时适用。
![[Pasted image 20260315002705.png]]

## 常见的工作流程
### 创建subagent
![[Pasted image 20260315015430.png]]
![[Pasted image 20260315015505.png]]


Claude Code skills存放的位置
![[Pasted image 20260315121344.png]]



## Model Context Protocol
安装MCP服务器
添加远程http服务器
HTTP 服务器是连接到远程 MCP 服务器的推荐选项。这是云服务最广泛支持的传输方式。
```shell
# 基本语法
claude mcp add --transport http <name> <url>

# 真实示例：连接到 Notion
claude mcp add --transport http notion https://mcp.notion.com/mcp

# 带有 Bearer 令牌的示例
claude mcp add --transport http secure-api https://api.example.com/mcp \
  --header "Authorization: Bearer your-token"
```

[添加本地stdio服务器](https://code.claude.com/docs/zh-CN/mcp#选项-3：添加本地-stdio-服务器)

[管理服务器](https://code.claude.com/docs/zh-CN/mcp#管理您的服务器)
![[Pasted image 20260315122926.png]]

[mcp安装范围](https://code.claude.com/docs/zh-CN/mcp#mcp-安装范围)
本地范围
本地范围的服务器代表默认配置级别，存储在您项目路径下的 `~/.claude.json` 中。这些服务器对您保持私密，仅在当前项目目录中工作时可访问。此范围非常适合个人开发服务器、实验配置或包含不应共享的敏感凭据的服务器。

```shell
# 添加本地范围的服务器（默认）
claude mcp add --transport http stripe https://mcp.stripe.com

# 显式指定本地范围
claude mcp add --transport http stripe --scope local https://mcp.stripe.com
```

项目范围
项目范围的服务器通过在项目根目录中存储配置在 `.mcp.json` 文件中来启用团队协作。此文件设计为检入版本控制，确保所有团队成员都可以访问相同的 MCP 工具和服务。添加项目范围的服务器时，Claude Code 会自动创建或更新此文件，使用适当的配置结构。

```shell
# 添加项目范围的服务器
claude mcp add --transport http paypal --scope project https://mcp.paypal.com/mcp
```
出于安全原因，Claude Code 在使用来自 `.mcp.json` 文件的项目范围的服务器之前会提示批准。如果您需要重置这些批准选择，请使用 `claude mcp reset-project-choices` 命令。

用户范围
用户范围的服务器存储在 `~/.claude.json` 中，并提供跨项目可访问性，使其在您机器上的所有项目中可用，同时对您的用户帐户保持私密。此范围适用于个人实用程序服务器、开发工具或您在不同项目中经常使用的服务。
```shell
# 添加用户服务器
claude mcp add --transport http hubspot --scope user https://mcp.hubspot.com/anthropic
```

选择正确的范围

根据以下条件选择您的范围：

- **本地范围**：个人服务器、实验配置或特定于一个项目的敏感凭据
- **项目范围**：团队共享的服务器、项目特定的工具或协作所需的服务
- **用户范围**：跨多个项目需要的个人实用程序、开发工具或经常使用的服务

> [!info] MCP 服务器存储在哪里？
> - **用户和本地范围**：`~/.claude.json`（在 `mcpServers` 字段或项目路径下）
> - **项目范围**：项目根目录中的 `.mcp.json`（检入源代码控制）
> - **托管**：系统目录中的 `managed-mcp.json`（请参阅[托管 MCP 配置](https://code.claude.com/docs/zh-CN/mcp#managed-mcp-configuration)）







## 基本命令
[快速入门](https://code.claude.com/docs/zh-CN/quickstart)
### 基本命令
以下是日常使用中最重要的命令：

| 命令                  | 功能             | 示例                                  |
| ------------------- | -------------- | ----------------------------------- |
| `claude`            | 启动交互模式         | `claude`                            |
| `claude "task"`     | 运行一次性任务        | `claude "fix the build error"`      |
| `claude -p "query"` | 运行一次性查询，然后退出   | `claude -p "explain this function"` |
| `claude -c`         | 在当前目录中继续最近的对话  | `claude -c`                         |
| `claude -r`         | 恢复之前的对话        | `claude -r`                         |
| `claude commit`     | 创建 Git 提交      | `claude commit`                     |
| `/clear`            | 清除对话历史         | `> /clear`                          |
| `/help`             | 显示可用命令         | `> /help`                           |
| `exit` 或 Ctrl+C     | 退出 Claude Code | `> exit`                            |
补充
```python
/exit | /quit 退出对话
/resume 查看对话历史
/model 查看当前使用的模型
/compact 压缩对话
/clear 清除对话记录
！ 添加冒号可以执行命令
```
有关完整的命令列表，请参阅 [CLI 参考](https://code.claude.com/docs/zh-CN/cli-reference)。
## CC基本操作
![[Pasted image 20260209223411.png]]
### 中断cc和引导
![[Pasted image 20260209224017.png]]
### cc扩展配置
![[Pasted image 20260210164652.png]]
![[Pasted image 20260210164704.png]]
### claude code常见工作流程
[官方常见工作流程文档](https://code.claude.com/docs/zh-CN/common-workflows#%E7%90%86%E8%A7%A3%E6%96%B0%E4%BB%A3%E7%A0%81%E5%BA%93)
### 使用会话选择器
![[Pasted image 20260210171045.png]]
### 最佳实践
[官方最佳实践](https://code.claude.com/docs/zh-CN/best-practices)
#### `CLAUDE.md`文件放置的位置
![[Pasted image 20260210171858.png]]

#### 管理上下文
当你接近上下文限制时，Claude Code 会自动压缩对话历史，这保留了重要的代码和决策，同时释放空间。在长会话中，Claude 的 context window 可能会被无关的对话、文件内容和命令填满。这可能会降低性能，有时会分散 Claude 的注意力。
- 在任务之间频繁使用 `/clear` 以完全重置 context window
- 当自动压缩触发时，Claude 总结最重要的内容，包括代码模式、文件状态和关键决策
- 为了更好地控制，运行 `/compact <instructions>`，如 `/compact Focus on the API changes`
- 在 CLAUDE.md 中自定义压缩行为，使用像 `"When compacting, always preserve the full list of modified files and any test commands"` 这样的指令，以确保关键上下文在总结中幸存

### CC的三种模式
![[Pasted image 20260210231345.png]]
windows快捷键: `alt + m`
#### 命令行模式
![[Pasted image 20260210231521.png]]
#### 危险模式
![[Pasted image 20260210232134.png]]

### cc后台运行任务
>任务后台运行， 不阻塞当前窗口

![[Pasted image 20260210232459.png]]

### cc回滚
按两下`esc`，或者输入`\rewind`就可以查看回滚点并选择回滚方式
- 列出回滚点
	![[Pasted image 20260210233038.png]]

- 选择回滚方式
	![[Pasted image 20260210233427.png]]

### cc浏览图片
cc阅读图片方式，第一种是直接拖动，第一种是`ctrl + v`粘贴图片进去

### cc查看ui设计稿图并复现
> [见教学视频这个节点附近](https://www.bilibili.com/video/BV14rzQB9EJj/?spm_id_from=333.337.search-card.all.click&vd_source=f206e98233aae099adecce9377d98cc2)
![[Pasted image 20260210233811.png]]

### cc上下文记忆`CLAUDE.md`
![[Pasted image 20260210234139.png]]

## 优秀CC学习教程和资料

### 视频
![[Pasted image 20260210225948.png]]
[Claude Code 从 0 到 1 全攻略：MCP / SubAgent / Agent Skill / Hook / 图片 / 上下文处理/ 后台任务_哔哩哔哩_bilibili](https://www.bilibili.com/video/BV14rzQB9EJj/?spm_id_from=333.337.search-card.all.click&vd_source=f206e98233aae099adecce9377d98cc2)
[# 最火AI编程Claude Code详细攻略，一期视频精通](https://www.bilibili.com/video/BV1XGbazvEuh/?spm_id_from=333.337.search-card.all.click&vd_source=f206e98233aae099adecce9377d98cc2)

### 文章
[10分钟掌握Claude Code所有命令指南 ​]( https://www.claude-cn.org/posts/Claude-code-commands-guide.html#_3%EF%B8%8F%E2%83%A3-mcp%E5%91%BD%E4%BB%A4-%E8%AE%A9claude-code%E5%BC%80%E6%8C%82-%E2%80%8B)
[Claude Code 超详细完整指南](https://blog.csdn.net/weixin_52136627/article/details/149719262)
[Claude Code 添加 MCP 服务器完整指南](https://zhuanlan.zhihu.com/p/1933624323849032925)


## CC MCP相关
[通过 MCP 将 Claude Code 连接到工具](https://code.claude.com/docs/zh-CN/mcp)
### mcp的安装范围
https://code.claude.com/docs/zh-CN/mcp#mcp-安装范围
注意，本地范围和用户范围的mcp服务配置都是放到同一个文件下，但是存放的字段有差异
![[Pasted image 20260222142516.png]]

### 常用的mcp工具
`context7`
https://github.com/upstash/context7
```
api-key: ctx7sk-5c9dc3a5-88f4-44fa-998c-6a183347a8ab
```


## CC配置文件作用域
![[Pasted image 20260222161704.png]]
[可用作用域](https://code.claude.com/docs/zh-CN/settings#可用作用域)
### [作用域如何相互作用](https://code.claude.com/docs/zh-CN/settings#作用域如何相互作用)
当在多个作用域中配置相同的设置时，更具体的作用域优先：
1. **Managed**（最高）- 无法被任何内容覆盖
2. **命令行参数** - 临时会话覆盖
3. **Local** - 覆盖项目和用户设置
4. **Project** - 覆盖用户设置
5. **User**（最低）- 当没有其他内容指定设置时应用
>例如，如果在用户设置中允许某个权限，但在项目设置中拒绝，则项目设置优先，权限被阻止。
### [哪些功能使用作用域](https://code.claude.com/docs/zh-CN/settings#哪些功能使用作用域)
![[Pasted image 20260222162057.png]]



cc思考强度
![[Pasted image 20260222145320.png]]

## CC其他特性
配置文件储存位置
cc自定义命令
cc hook
cc agent
github cli
ccundo
claudia


openclaw
opencode
openrouter
cc switch
## CC plugin
https://code.claude.com/docs/zh-CN/plugins
### 在anthripic官方插件市场安装插件
https://code.claude.com/docs/zh-CN/discover-plugins#官方-anthropic-市场

## CC Skills
官方Skills介绍这里：[注入动态上下文](https://code.claude.com/docs/zh-CN/skills#注入动态上下文), CC是如何执行命令的，在自己的Bash里面我？


## CC Memory
https://code.claude.com/docs/zh-CN/memory


## CC Hooks
特定事件发生时候执行命令
hook相关的参考：https://code.claude.com/docs/zh-CN/hooks

## 问题
如何让claude链接外部文档
什么是mcp
什么是skills
如何让claude code使用上述两个
claude code中的subagents、plugins

ccusage查看模型使用量


claude code资源
https://easyclaude.com/

