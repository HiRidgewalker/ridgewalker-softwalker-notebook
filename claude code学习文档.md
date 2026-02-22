## 快速入门
https://code.claude.com/docs/zh-CN/quickstart
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

有关完整的命令列表，请参阅 [CLI 参考](https://code.claude.com/docs/zh-CN/cli-reference)。

![[Pasted image 20260209223411.png]]

![[Pasted image 20260209224017.png]]

### 扩展配置
![[Pasted image 20260210164652.png]]
![[Pasted image 20260210164704.png]]
### claude code常见工作流程
[资源链接](https://code.claude.com/docs/zh-CN/common-workflows#%E7%90%86%E8%A7%A3%E6%96%B0%E4%BB%A3%E7%A0%81%E5%BA%93)

使用会话选择器
![[Pasted image 20260210171045.png]]

### 最佳实践
https://code.claude.com/docs/zh-CN/best-practices

#### claude code的`CLAUDE.md`文件放置的位置
![[Pasted image 20260210171858.png]]

#### 积极的管理上下文
当你接近上下文限制时，Claude Code 会自动压缩对话历史，这保留了重要的代码和决策，同时释放空间。在长会话中，Claude 的 context window 可能会被无关的对话、文件内容和命令填满。这可能会降低性能，有时会分散 Claude 的注意力。

- 在任务之间频繁使用 `/clear` 以完全重置 context window
- 当自动压缩触发时，Claude 总结最重要的内容，包括代码模式、文件状态和关键决策
- 为了更好地控制，运行 `/compact <instructions>`，如 `/compact Focus on the API changes`
- 在 CLAUDE.md 中自定义压缩行为，使用像 `"When compacting, always preserve the full list of modified files and any test commands"` 这样的指令，以确保关键上下文在总结中幸存

## 视频教程
![[Pasted image 20260210225948.png]]
[Claude Code 从 0 到 1 全攻略：MCP / SubAgent / Agent Skill / Hook / 图片 / 上下文处理/ 后台任务_哔哩哔哩_bilibili](https://www.bilibili.com/video/BV14rzQB9EJj/?spm_id_from=333.337.search-card.all.click&vd_source=f206e98233aae099adecce9377d98cc2)

claude code的3种模式
![[Pasted image 20260210231345.png]]
windows快捷键: `alt + m`

命令行模式
![[Pasted image 20260210231521.png]]

危险模式
![[Pasted image 20260210232134.png]]

任务后台运行， 不阻塞当前窗口
![[Pasted image 20260210232459.png]]

claude code回滚
按两下`esc`，或者输入`\rewind`就可以查看回滚点并选择回滚方式
回滚点
![[Pasted image 20260210233038.png]]

选择回滚方式
![[Pasted image 20260210233427.png]]

cc阅读图片方式，第一种是直接拖动，第一种是`ctrl + v`粘贴图片进去

使用mcp + figma快速还原设计稿案例
> 见上述教学视频
这个节点附近
![[Pasted image 20260210233811.png]]


上下文压缩和清空 `/compact`和`/clear`, 还有恢复对话和选择对话


cc上下文记忆`CLAUDE.md`
![[Pasted image 20260210234139.png]]

`/hooks`

`/skills`

`claude code`


skills
mcp
subagent
hook
tool
plugin


## 补充
```python
/exit | /quit 退出对话
/resume 查看对话历史
/model 查看当前使用的模型
/compact 压缩对话
/clear 清除对话记录
！ 添加冒号可以执行命令
```
`!`: 输入执行命令
![[Pasted image 20251215002534.png]]

`#`:长期记忆
![[Pasted image 20251215002636.png]]

claude code教程文章和视频
文章1: https://www.claude-cn.org/posts/Claude-code-commands-guide.html#_3%EF%B8%8F%E2%83%A3-mcp%E5%91%BD%E4%BB%A4-%E8%AE%A9claude-code%E5%BC%80%E6%8C%82-%E2%80%8B

文章2:https://blog.csdn.net/weixin_52136627/article/details/149719262

视频：[视频教程](https://www.bilibili.com/video/BV1XGbazvEuh/?spm_id_from=333.337.search-card.all.click&vd_source=f206e98233aae099adecce9377d98cc2)


claude code mcp新手教程
https://zhuanlan.zhihu.com/p/1933624323849032925



## 问题
如何让claude链接外部文档

什么是mcp
什么是skills
如何让claude code使用上述两个
claude code中的subagents、plugins

hello llm

hello world

