CodeX官方文档
https://developers.openai.com/codex/prompting

Claude Code的记忆文件是**CLAUDE.md**, CodeX是**AGENTS.md**

`AGENTS.md` 为 Codex 提供持久的项目指南，该指南会随您的代码库一起传输，并在代理开始工作之前应用。请保持其简洁性

codex agents.md文件位置
![[Pasted image 20260316155848.png]]

codex skills位置
![[Pasted image 20260316155940.png]]

codex的沙箱模式
`read-only` ：Codex 可以查看文件，但未经批准不能编辑文件或运行命令。
`workspace-write` ：Codex 可以读取文件、在工作区内进行编辑，并在该边界内运行常规的本地命令。这是本地工作的默认低摩擦模式。
`danger-full-access` ：Codex 在无沙箱限制的情况下运行。这将移除文件系统和网络边界，仅当您希望 Codex 拥有完全访问权限时才应使用此功能。

web search
Codex 自带一个原生网络搜索工具。对于 Codex CLI 中的本地任务，Codex 默认启用网络搜索，并从网络搜索缓存中提供结果。该缓存是由 OpenAI 维护的网络搜索结果索引，因此缓存模式返回的是预先索引的结果，而不是实时获取页面。这降低了从任意实时内容中获取提示注入的风险，但您仍然应该将网络搜索结果视为不可信。如果您使用 `--yolo` 或其他[完全访问沙箱设置](https://developers.openai.com/codex/agent-approvals-security) ，则网络搜索默认使用实时结果。要获取最新数据，请在单次运行中传递 `--search` ，或在[配置基础设置](https://developers.openai.com/codex/config-basic)中将 `web_search = "live"` 。您也可以将 `web_search = "disabled"` 来关闭该工具。


codex 在用户级别和项目级别配置MCP
![[Pasted image 20260316163426.png]]




