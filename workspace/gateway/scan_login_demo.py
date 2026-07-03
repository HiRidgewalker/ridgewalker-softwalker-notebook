"""
扫码登录 demo（PC + 移动 App 模拟）。

演示（对应 [[鉴权与登录笔记]] §4）：
- 5 步完整流程：生成二维码 → 轮询状态 → App 确认 → 用 code 换 token
- qr_token 服务端 HMAC 签名（防伪造）
- 二维码过期、一次性 login_code

启动：
    # 终端 1：起服务端（PC 端 + App 端 API 都由它提供）
    .venv/bin/python workspace/gateway/scan_login_demo.py

    # 终端 2：模拟 PC 端（生成 + 轮询）
    .venv/bin/python -c "from workspace.gateway.scan_login_demo import demo_pc; demo_pc()"

或者直接访问浏览器端（见 README）
"""
from __future__ import annotations

import json
import logging
import secrets
import threading
import time
from datetime import datetime, timedelta, timezone

import jwt
import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] scan-login | %(message)s",
)
logger = logging.getLogger("scan-login")


# ============================================================
# 配置
# ============================================================
SECRET = "scan-login-demo-secret"
ALG = "HS256"
QR_TTL_SEC = 90             # 二维码有效期
LOGIN_CODE_TTL_SEC = 30     # login_code 有效期

# 内存存储（生产用 Redis）
QR_STORE: dict[str, dict] = {}            # qr_id -> {status, login_code, sub, ...}
USER_TOKENS: dict[str, dict] = {}         # sub -> {access, refresh}


# ============================================================
# 工具
# ============================================================
def _now() -> datetime:
    return datetime.now(tz=timezone.utc)


def issue_tokens(sub: str) -> dict:
    """签发双 token（demo 简化版）。"""
    access = jwt.encode(
        {"sub": sub, "exp": _now() + timedelta(minutes=15), "type": "access"},
        SECRET, algorithm=ALG,
    )
    refresh = jwt.encode(
        {"sub": sub, "exp": _now() + timedelta(days=7), "type": "refresh"},
        SECRET, algorithm=ALG,
    )
    USER_TOKENS[sub] = {"access": access, "refresh": refresh}
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}


def cleanup_expired():
    """定期清理过期的二维码。"""
    while True:
        time.sleep(10)
        now = time.time()
        expired = [q for q, info in QR_STORE.items()
                   if info["expires_at"] < now]
        for q in expired:
            QR_STORE.pop(q, None)
            logger.info("cleaned up expired qr_id=%s", q)


# ============================================================
# FastAPI 应用
# ============================================================
app = FastAPI(title="Scan Login Demo")

cleanup_thread = threading.Thread(target=cleanup_expired, daemon=True)
cleanup_thread.start()


# ----- 1. PC 端：生成二维码 -----
@app.get("/qr/generate")
def generate_qrcode():
    """PC 端第一步：生成二维码 ID + 二维码内容（签名 token）。

    PC 端把 qr_content 渲染成二维码（用 qrcode.js 或类似库）。
    """
    qr_id = secrets.token_urlsafe(16)

    # qr_token 是签名后的 token，App 端扫码后提取并回传服务端验证
    qr_token = jwt.encode(
        {
            "qr_id": qr_id,
            "exp": _now() + timedelta(seconds=QR_TTL_SEC),
            "nonce": secrets.token_urlsafe(8),
        },
        SECRET, algorithm=ALG,
    )

    QR_STORE[qr_id] = {
        "status": "waiting_scan",           # waiting_scan -> scanned -> confirmed -> done
        "sub": None,
        "login_code": None,
        "expires_at": time.time() + QR_TTL_SEC,
        "created_at": _now().isoformat(),
    }

    # 实际生产这里返回的是要渲染成二维码的 URL（含 qr_token）
    qr_content = f"https://yourapp.com/qr/scan?qr_id={qr_id}&sig={qr_token}"

    return {
        "qr_id": qr_id,
        "qr_content": qr_content,
        "expires_in": QR_TTL_SEC,
        "poll_url": f"/qr/status/{qr_id}",
    }


# ----- 2. PC 端：轮询状态 -----
@app.get("/qr/status/{qr_id}")
def poll_status(qr_id: str):
    """PC 端第二步：每 2 秒轮询一次。

    状态机：
        waiting_scan → 用户还没扫
        scanned      → 用户已扫但还没确认
        confirmed    → 用户已确认，返回 login_code
        done         → PC 已用 login_code 换过 token
        expired      → 二维码过期
    """
    info = QR_STORE.get(qr_id)
    if not info:
        return JSONResponse(
            {"status": "expired", "detail": "qrcode not found or expired"},
            status_code=404,
        )
    if info["expires_at"] < time.time():
        return {"status": "expired"}

    response = {"status": info["status"]}
    if info["status"] == "confirmed":
        response["login_code"] = info["login_code"]
        # 给 PC 端一些时间用 login_code 换 token，之后标记 done
        # 这里简化：直接标记 done
        info["status"] = "done"
    return response


# ----- 3. App 端：扫码并确认登录 -----
class ScanRequest(BaseModel):
    qr_id: str
    qr_token: str          # 二维码里的签名 token
    sub: str               # 当前 App 已登录的用户（生产从 App session 取）


@app.post("/qr/scan")
def scan_and_confirm(req: ScanRequest):
    """App 端第三步：扫码 + 确认登录。

    App 已登录，扫码后携带 App 端用户身份。
    """
    # 验证 qr_token 签名
    try:
        payload = jwt.decode(req.qr_token, SECRET, algorithms=[ALG])
        if payload["qr_id"] != req.qr_id:
            raise HTTPException(400, "qr_id mismatch")
    except jwt.ExpiredSignatureError:
        raise HTTPException(400, "qrcode expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(400, f"invalid qr_token: {e}")

    info = QR_STORE.get(req.qr_id)
    if not info or info["expires_at"] < time.time():
        raise HTTPException(404, "qrcode not found or expired")

    # 标记已扫码
    info["status"] = "scanned"
    info["scanned_sub"] = req.sub
    info["scanned_at"] = _now().isoformat()

    # demo 简化：直接进入 confirmed（真实场景需要 App 上点击"确认登录"）
    info["status"] = "confirmed"
    info["login_code"] = secrets.token_urlsafe(32)
    info["sub"] = req.sub
    info["login_code_expires_at"] = time.time() + LOGIN_CODE_TTL_SEC

    return {"ok": True, "status": info["status"]}


# ----- 4. PC 端：用 login_code 换 token -----
class LoginRequest(BaseModel):
    qr_id: str
    login_code: str


@app.post("/qr/login")
def exchange_login_code(req: LoginRequest):
    """PC 端第四步：用 login_code 换 access + refresh token。

    login_code 一次性，使用后立即失效。
    """
    info = QR_STORE.get(req.qr_id)
    if not info:
        raise HTTPException(404, "qrcode not found")
    if info["status"] != "done":
        raise HTTPException(400, f"status is {info['status']}, expected done")
    if info["login_code"] != req.login_code:
        raise HTTPException(400, "invalid login_code")
    if info["login_code_expires_at"] < time.time():
        raise HTTPException(400, "login_code expired")

    sub = info["sub"]
    info["login_code"] = None                # 一次性，使用后失效
    tokens = issue_tokens(sub)

    return {**tokens, "sub": sub, "logged_in": True}


# ----- 5. 浏览器端 demo 页面 -----
@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse("""
<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>扫码登录 Demo</title>
<style>
body { font-family: -apple-system, sans-serif; max-width: 720px; margin: 30px auto; padding: 0 16px; }
.box { border: 1px solid #ddd; padding: 16px; margin: 12px 0; border-radius: 4px; }
button { padding: 8px 16px; font-size: 14px; cursor: pointer; }
pre { background: #f5f5f5; padding: 10px; overflow-x: auto; font-size: 12px; }
h2 { font-size: 16px; margin: 0 0 8px 0; }
</style>
</head><body>
<h1>扫码登录 Demo</h1>

<div class="box">
<h2>Step 1: PC 端生成二维码</h2>
<button onclick="step1()">生成二维码</button>
<pre id="qr-result">（点击按钮生成）</pre>
</div>

<div class="box">
<h2>Step 2: 模拟 App 扫码（已登录为 alice）</h2>
<input id="qr-id" placeholder="粘贴 qr_id" style="width: 300px">
<input id="qr-token" placeholder="粘贴 sig" style="width: 400px">
<button onclick="step3()">App 扫码 + 确认</button>
<pre id="scan-result">（点击按钮模拟扫码）</pre>
</div>

<div class="box">
<h2>Step 3: PC 端轮询 → 获得 login_code</h2>
<button onclick="step2()">轮询状态</button>
<pre id="poll-result">（点击按钮轮询）</pre>
</div>

<div class="box">
<h2>Step 4: PC 端用 login_code 换 token</h2>
<input id="login-code" placeholder="粘贴 login_code" style="width: 400px">
<button onclick="step4()">换 token</button>
<pre id="token-result">（点击按钮换 token）</pre>
</div>

<script>
let currentQrId = null;

async function step1() {
    const r = await fetch('/qr/generate');
    const data = await r.json();
    currentQrId = data.qr_id;
    document.getElementById('qr-result').textContent = JSON.stringify(data, null, 2);
    document.getElementById('qr-id').value = data.qr_id;
    document.getElementById('qr-token').value = data.qr_content.split('sig=')[1];
}

async function step3() {
    const qr_id = document.getElementById('qr-id').value;
    const qr_token = document.getElementById('qr-token').value;
    const r = await fetch('/qr/scan', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({qr_id, qr_token, sub: 'alice'}),
    });
    const data = await r.json();
    document.getElementById('scan-result').textContent = JSON.stringify(data, null, 2);
}

async function step2() {
    if (!currentQrId) { alert('先生成二维码'); return; }
    const r = await fetch('/qr/status/' + currentQrId);
    const data = await r.json();
    document.getElementById('poll-result').textContent = JSON.stringify(data, null, 2);
    if (data.login_code) {
        document.getElementById('login-code').value = data.login_code;
    }
}

async function step4() {
    const login_code = document.getElementById('login-code').value;
    const r = await fetch('/qr/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({qr_id: currentQrId, login_code}),
    });
    const data = await r.json();
    document.getElementById('token-result').textContent = JSON.stringify(data, null, 2);
}
</script>
</body></html>
""")


# ============================================================
# CLI 测试函数
# ============================================================
def demo_pc():
    """命令行模拟 PC 端 4 步流程。"""
    import requests

    base = "http://127.0.0.1:9009"

    print("\n[1] PC 生成二维码")
    r = requests.get(f"{base}/qr/generate").json()
    print(json.dumps(r, indent=2, ensure_ascii=False))
    qr_id = r["qr_id"]
    qr_token = r["qr_content"].split("sig=")[1]

    print("\n[2] PC 轮询（等待扫描）")
    s = requests.get(f"{base}/qr/status/{qr_id}").json()
    print(json.dumps(s, indent=2, ensure_ascii=False))

    print("\n[3] 模拟 App 扫码（App 当前登录用户是 alice）")
    r = requests.post(
        f"{base}/qr/scan",
        json={"qr_id": qr_id, "qr_token": qr_token, "sub": "alice"},
    ).json()
    print(json.dumps(r, indent=2, ensure_ascii=False))

    print("\n[4] PC 轮询 → 获得 login_code")
    s = requests.get(f"{base}/qr/status/{qr_id}").json()
    print(json.dumps(s, indent=2, ensure_ascii=False))

    print("\n[5] PC 用 login_code 换 token")
    r = requests.post(
        f"{base}/qr/login",
        json={"qr_id": qr_id, "login_code": s["login_code"]},
    ).json()
    print(json.dumps(r, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9009, log_level="info")