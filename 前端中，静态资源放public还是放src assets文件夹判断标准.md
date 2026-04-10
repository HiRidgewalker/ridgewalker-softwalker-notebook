• 核心判断标准不是“图片还是字体”，而是“这个资源要不要进入模块打包系统”。

  放 public/ 的资源，适合这些情况：

  - 需要固定 URL 直接访问，比如 /favicon.svg、/robots.txt、/manifest.webmanifest
  - 不想经过 Vite/Webpack 打包处理
  - 你希望文件名保持不变，方便外部系统或浏览器按约定读取
  - 运行时动态拼接路径更方便，比如后端返回 /images/a.png 这类静态地址

  典型例子：

  - favicon.ico / favicon.svg
  - robots.txt
  - sitemap.xml
  - manifest.json
  - 第三方要求固定文件名的验证文件
  - 很大的静态素材库，且你不想让它们被 import 进构建图

  放 src/assets/ 的资源，适合这些情况：

  - 这个资源会被组件 import
  - 希望打包器帮你做指纹文件名、缓存优化、路径重写
  - 资源和某个页面/组件强关联，属于源码的一部分
  - 你希望未使用资源能被更好地跟随源码管理

  典型例子：

  - 组件里引用的图片、图标、插图
  - 本地字体文件
  - 页面背景图
  - 某个模块专用的音频、视频、svg

  例如：

  import heroImage from './assets/hero.png'

  export function Hero() {
    return <img src={heroImage} alt="hero" />
  }

  简单记忆：

  - public/：面向“网站公开目录”的静态文件
  - src/assets/：面向“源码模块引用”的静态文件