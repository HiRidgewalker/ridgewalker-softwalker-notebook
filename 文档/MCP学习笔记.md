## MCP资源
**官方mcp文档**
[https://github.com/modelcontextprotocol](https://github.com/modelcontextprotocol)

**官方python sdk文档**
https://py.sdk.modelcontextprotocol.io/

**官方mcp server收集平台**
https://github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)

**社区mcp收集平台**
- [https://bailian.console.aliyun.com/tab=mcp#/mcp-market](https://bailian.console.aliyun.com/tab=mcp#/mcp-market)
- https://smithery.ai/servers
- [https://mcp.so/zh](https://mcp.so/zh)
- [https://github.com/punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers)
- [https://learn.microsoft.com/api/mcp](https://learn.microsoft.com/api/mcp)

**MCP中文资源**
[MCPcn.com](https://mcpcn.com/)

## MCP常见的三种通信方式/传输方式
- **stdio**
    - 本地进程通信
    - MCP Server 通过标准输入 / 标准输出和 Client 通信
    - 最常见，适合本地工具，比如文件系统、Git、数据库本地访问
- **SSE**
    - 全称 **Server-Sent Events**
    - 基于 HTTP，服务端通过 SSE 向客户端推送消息
    - 现在偏旧，很多文档里会叫 **legacy SSE transport**
- **Streamable HTTP**
    - 也叫 **HTTP transport / Streaming HTTP / Streamable HTTP**
    - 这是现在 MCP 更推荐的远程通信方式
    - 使用 HTTP POST / GET，请求更标准，也可以可选地用 SSE 做流式返回


