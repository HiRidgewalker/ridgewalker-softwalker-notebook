# 下载问题总结
## cuda
cuda下载网站: [https://developer.nvidia.com/cuda-toolkit](https://developer.nvidia.com/cuda-toolkit)
命令`nvidia-smi`查看当前电脑显卡信息：
![](https://cdn.nlark.com/yuque/0/2025/png/38690142/1747903668818-cc0a0913-3f0d-4f2c-9922-f3136b448964.png)
>注意： 这里的cuda版本表示驱动支持的CUDA Runtime 最高支持版本 但是不代表你已经安装了它

命令`nvcc --version`查看安装的cuda toolkit版本信息
![](https://cdn.nlark.com/yuque/0/2025/png/38690142/1747904169719-ef950a71-a6e8-430b-b6ff-7c708a94ba15.png)
## cudnn下载
[2025 CUDA 和 cuDNN 在 Windows 上如何安装配置（保姆级详细版）_windows安装cuda-CSDN博客](https://blog.csdn.net/m0_66434421/article/details/147337716)

## torch下载
torch whl下载网址: [download.pytorch.org/whl/torch_stable.html](https://download.pytorch.org/whl/torch_stable.html)
相关文章: [【超详细教程】2025年3月最新Pytorch安装教程（同时讲解安装CPU和GPU版本）-CSDN博客](https://blog.csdn.net/Mr_Chp/article/details/146641434)


## 学习torch遇到的知识点
`雅各比矩阵`
[(27 封私信 / 80 条消息) 基本初等函数导数推导 - 知乎](https://zhuanlan.zhihu.com/p/89843248) 
CNN（卷积）
- 卷积核
- 池化


## 网络模型的部位分类
网络模型分为主干网络，颈部网络和头部网络
![[Pasted image 20260206105625.png]]

`__call__`方法

