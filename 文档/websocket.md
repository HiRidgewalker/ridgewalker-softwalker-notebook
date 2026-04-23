## webwebsocket特性
<font style="color:rgb(17, 17, 17);background-color:rgb(245, 245, 213);">服务器可以主动向客户端推送信息，客户端也可以主动向服务器发送信息，是真正的双向平等对话，属于服务推送技术的一种</font>

<!-- 这是一张图片，ocr 内容为： -->
![](https://cdn.nlark.com/yuque/0/2024/png/38690142/1733235106736-350cff80-e77a-43cb-a722-f9bec8cb069b.png)

<font style="color:rgb(17, 17, 17);background-color:rgb(245, 245, 213);">其他特点：</font>

<font style="color:rgb(17, 17, 17);background-color:rgb(245, 245, 213);">其他特点包括：</font>

<font style="color:rgb(17, 17, 17);background-color:rgb(245, 245, 213);">（1）建立在 TCP 协议之上，服务器端的实现比较容易。</font>

<font style="color:rgb(17, 17, 17);background-color:rgb(245, 245, 213);">（2）与 HTTP 协议有着良好的兼容性。默认端口也是80和443，并且握手阶段采用 HTTP 协议，因此握手时不容易屏蔽，能通过各种 HTTP 代理服务器。</font>

<font style="color:rgb(17, 17, 17);background-color:rgb(245, 245, 213);">（3）数据格式比较轻量，性能开销小，通信高效。</font>

<font style="color:rgb(17, 17, 17);background-color:rgb(245, 245, 213);">（4）可以发送文本，也可以发送二进制数据。</font>

<font style="color:rgb(17, 17, 17);background-color:rgb(245, 245, 213);">（5）没有同源限制，客户端可以与任意服务器通信。</font>

<font style="color:rgb(17, 17, 17);background-color:rgb(245, 245, 213);">（6）协议标识符是</font>`<font style="color:rgb(17, 17, 17);background-color:#FFC0CB;">ws</font>`<font style="color:rgb(17, 17, 17);background-color:rgb(245, 245, 213);">（如果加密，则为</font>`<font style="color:rgb(17, 17, 17);background-color:#FFC0CB;">wss</font>`<font style="color:rgb(17, 17, 17);background-color:rgb(245, 245, 213);">），服务器网址就是 URL。</font>

```plain
ws://example.com:80/some/path
```

<font style="color:rgb(17, 17, 17);background-color:rgb(245, 245, 213);"></font>

## <font style="color:rgb(17, 17, 17);background-color:rgb(245, 245, 213);">相关文章</font>
[WebSocket 教程 - 阮一峰的网络日志](https://www.ruanyifeng.com/blog/2017/05/websocket.html)

