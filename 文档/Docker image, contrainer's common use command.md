## 平时积累的快捷命令
### mysql
```shell
docker run -d \
  --name mysql \
  -p 3306:3306 \
  -e TZ=Asia/Shanghai \
  -e MYSQL_ROOT_PASSWORD=root \
  mysql:8.0
  
  docker run -d \
  --name mysql \
  -p 3307:3306 \
  -e TZ=Asia/Shanghai \
  -e MYSQL_ROOT_PASSWORD=root \
  mysql:8.0
```
### redis
```shell
docker run \
  -v /home/docker-volume/redis/conf:/usr/local/etc/redis \
  -v /home/docker-volume/redis/data:/data \
  -p 6379:6379 \
  --name redis \
  -d \
  dockerproxy.cn/redis:7.4 \
  redis-server /usr/local/etc/redis/redis.conf
```
### docker ps指定输出格式
```shell
docker ps --format "table {{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}\t{{.Names}}"
```
### docker 启动容器
重启指定容器
```shell
docker restart <container_name_or_id>
```
先停止后启动
```shell
docker stop <container_name_or_id>
docker start <container_name_or_id>
```
重启所有正在运行的容器
```shell
docker restart $(docker ps -q)
```
### docker 挂载多个数据卷
```bash
docker run -p 80:5000 \
--mount type=bind,source=/home/user-one/pu-word-volume/docling-volume/tmp,target=/tmp \ 
--mount type=bind,source=/home/user-one/pu-word-volume/docling-volume/models,target=/app/models \
--mount type=bind,source=/home/user-one/pu-word-volume/static,target=/app/static \docling-basic-image:1.0 bash
docke```

/home/user-one/docker-file/docling/docling-volume
```bash
docling-tools models download -o /app/models
```


```bash
sudo docker run -it --mount type=bind,source=/home/user-one/docker-file/docling/docling-volume/models,target=/tmp --mount type=bind,source=/home/user-one/docker-file/docling/docling-volume/tmp,target=/app/models docling-basic-image:1.0 bash
```

```bash
sudo docker run -it --mount type=bind,source=/home/user-one/docker-file/docling/docling-volume/models,target=/tmp --mount type=bind,source=/home/user-one/docker-file/docling/docling-volume/tmp,target=/app/models docling-test:1.0 bash
```


libreoffice在容器中配置中文环境
```bash
# 更新包列表
apt-get update

# 安装中文字体包
apt-get install -y fonts-wqy-zenhei fonts-wqy-microhei fonts-noto-cjk

# 刷新字体缓存
fc-cache -fv

# 安装语言包
apt-get install -y locales

# 生成中文语言环境
locale-gen zh_CN.UTF-8

# 设置环境变量
export LANG=zh_CN.UTF-8
export LC_ALL=zh_CN.UTF-8

```