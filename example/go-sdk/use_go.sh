#!/usr/bin/env bash
# 启用 gvm 管理的 Go
# 用法：source example/go-sdk/use_go.sh
#
# 配合 gvm 的 go.mod 项目级版本控制：
#   - 项目里 go.mod 写 go 1.23.4
#   - 这个脚本默认启用 go1.23.4（与本仓库 demo 项目保持一致）
#   - 想切其他版本：gvm use go1.22.x

# shellcheck disable=SC1091
source "$HOME/.gvm/scripts/gvm"

gvm use go1.23.4

# GOPATH 必须 != GOROOT，否则 go 会警告
export GOPATH="$HOME/go-workspace"
export PATH="$GOPATH/bin:$PATH"
mkdir -p "$GOPATH"

echo "[use_go] go: $(go version)"
echo "[use_go] GOPATH: $GOPATH"
