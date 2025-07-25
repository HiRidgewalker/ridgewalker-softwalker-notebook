创建react项目，前端构建工具使用vite、同时给项目添加eslint、prettier插件
```text
**指令**：初始化React项目，配置Vite作为构建工具，集成ESLint代码检查和Prettier代码格式化插件。
**执行步骤**：
1. 使用Vite创建React项目模板
2. 安装并配置ESLint依赖包和规则集
3. 安装并配置Prettier依赖包和格式化规则
4. 配置ESLint与Prettier协同工作，避免规则冲突
5. 更新package.json添加相关脚本命令
```

添加tailwild css 框架
```text
**指令**：在现有React+Vite项目中集成Tailwind CSS v3，配置样式框架支持。

**执行步骤**：

1. 安装Tailwind CSS v3及其依赖包（tailwindcss、autoprefixer、postcss）
2. 初始化Tailwind配置文件（tailwind.config.js）
3. 创建PostCSS配置文件（postcss.config.js）
4. 在主CSS文件中引入Tailwind指令（@tailwind base/components/utilities）
5. 配置content路径以启用CSS purging优化
```

添加prettier配置文件
```text
**指令**：创建`.prettierrc`配置文件，设置缩进为4个空格，保持其他默认配置项。
```

