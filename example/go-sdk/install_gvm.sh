#!/usr/bin/env bash
# 安装 gvm + Go 1.23.4
# 用法：bash example/go-sdk/install_gvm.sh
#
# 前提：
#   - Ubuntu / Debian 系：sudo apt install -y bison
#   - 需要 curl、git、make
#   - 需要 sudo 安装 bison（编译 Go 源码要用）
set -euo pipefail

GO_VERSION="${GO_VERSION:-1.23.4}"

echo "==> 1. 安装 gvm 到 ~/.gvm"
bash < <(curl -s -S -L https://raw.githubusercontent.com/moovweb/gvm/master/binscripts/gvm-installer)

# gvm-installer 在 Ubuntu 上会拉 CRLF 格式的脚本，需要转成 LF
echo "==> 2. 修复 gvm 脚本的 CRLF 行尾"
find "$HOME/.gvm" -type f -exec sed -i 's/\r$//' {} +

# 加载 gvm
# shellcheck disable=SC1091
source "$HOME/.gvm/scripts/gvm"

echo "==> 3. 安装 Go ${GO_VERSION}（用 -B 装预编译版，避免源码编译需要的 bootstrap Go）"
gvm install "${GO_VERSION}" -B

echo "==> 4. 设置 ${GO_VERSION} 为默认版本"
gvm use "${GO_VERSION}" --default

echo ""
echo "==> 验证"
gvm list
go version

echo ""
echo "==> 下一步：新开一个 shell，启用 Go"
echo "    source example/go-sdk/use_go.sh"
