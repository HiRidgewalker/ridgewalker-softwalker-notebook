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
