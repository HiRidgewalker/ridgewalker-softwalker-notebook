一个python的包管理器: [UV](https://docs.astral.sh/uv/getting-started/installation/)

## 升级uv
```shelle
uv self update
```
## uninstalltion
```shell
uv cache clean
rm -r "$(uv python dir)"
rm -r "$(uv tool dir)"
```
## 删除uv和uvx二进制文件
```shell
rm $HOME\.local\bin\uv.exe
rm $HOME\.local\bin\uvx.exe
```
## UV常用命令
[UV常用命令](https://docs.astral.sh/uv/getting-started/features/)
UV安装python
```shell
-- 安装特定版本
uv python install 3.12

-- 安装多个版本
uv python install 3.11, 3.12
```



