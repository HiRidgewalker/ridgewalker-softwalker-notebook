#!/bin/sh
# 测试脚本：向 3 种挂载各写入一个文件并打印时间
set -e

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
PAYLOAD="written at $TIMESTAMP by container $$(hostname)"

echo "writing to each mount..."
for MOUNT in bind volume tmpfs; do
    case "$MOUNT" in
        bind)  DIR=/in-bind ;;
        volume) DIR=/in-volume ;;
        tmpfs) DIR=/in-tmpfs ;;
    esac

    # tmpfs 第一次写之前，可能不存在；确保有目录
    if [ "$MOUNT" = "tmpfs" ]; then
        mkdir -p "$DIR"
    fi

    echo "$PAYLOAD" > "$DIR/hello.txt"
    echo "[$MOUNT] wrote: $(cat "$DIR/hello.txt")"
done

echo "sleeping 60s, do:"
echo "  docker compose -f example/docker/03_volume_demo/compose.yml exec inspector sh"
echo "  ls -l /inspect-bind /inspect-volume"

sleep 60
