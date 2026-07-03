/*
 * Node.js WebSocket 客户端示例。
 *
 * 演示：
 * - 连接服务端
 * - 发送 + 接收消息
 * - 心跳
 *
 * 对应笔记：[[Hub/websocket笔记]] 第 6.3 节
 *
 * 安装：
 *   npm install ws
 *
 * 启动：
 *   node workspace/ws/client_js_console.js
 */

const WebSocket = require("ws");

const CLIENT_ID = "node_bob";
const TOKEN = "demo_token_123";
const URI = `ws://localhost:8000/ws/${CLIENT_ID}?token=${TOKEN}`;

const ws = new WebSocket(URI);

ws.on("open", () => {
  console.log("connected:", CLIENT_ID);

  // 应用层心跳（30s 一次）
  setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send('{"type":"ping"}');
    }
  }, 30000);

  // 周期性发消息
  let i = 0;
  setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(`hello from node #${i++}`);
    }
  }, 3000);
});

ws.on("message", (data) => {
  const text = data.toString();
  if (text === '{"type":"pong"}') return;       // 心跳忽略
  console.log("[recv]", text);
});

ws.on("close", (code, reason) => {
  console.log(`disconnected: code=${code} reason=${reason.toString()}`);
});

ws.on("error", (err) => {
  console.error("[error]", err.message);
});

// Ctrl+C 优雅退出
process.on("SIGINT", () => {
  console.log("\nclosing...");
  ws.close();
  setTimeout(() => process.exit(0), 500);
});