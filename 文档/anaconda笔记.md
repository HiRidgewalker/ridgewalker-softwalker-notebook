## conda使用手册
> [https://docs.conda.io/projects/conda/en/latest/user-guide/index.html](https://docs.conda.io/projects/conda/en/latest/user-guide/index.html)
>

## anaconda和miniconda的区别
> <font style="color:rgb(206, 214, 221);background-color:rgba(255, 255, 255, 0);"> </font><font style="background-color:rgba(255, 255, 255, 0);">Anaconda Distribution 自动安装 300 多个此类软件包，而 Miniconda 是一个更轻量级的发行版，仅包含 conda、python、它们的依赖项和少量其他软件包。</font>
>

## <font style="background-color:rgba(255, 255, 255, 0);">和conda的命令行一起工作</font>
### 环境
#### 创建环境
```python
# 创建一个空的python环境
# Replace <ENV_NAME> with a name for your environment
conda create -n <ENV_NAME>

# 创建一个包含python和package的环境
# Replace <ENV_NAME> with a name for your environment
# Replace <PACKAGE> with your desired package
# Replace <VERSION> with your desired version of Python
conda create -n <ENV_NAME> python=<VERSION> <PACKAGE>=<VERSION>


```

#### 激活环境
<font style="color:#262626;">由于环境是孤立的空间，因此您一次只能使用一个空间。选择要使用的环境称为激活它。</font>

```python
# Replace <ENV_NAME> with the name of the environment you want to activate
conda activate <ENV_NAME>
```

#### <font style="color:#262626;background-color:rgba(255, 255, 255, 0);">环境切换</font>
通过运行命令查看所有环境

```python
conda info --envs
或
conda env list
```

切换到不同的环境

```python
# Replace <ENV_NAME> with the name of the environment you want to switch to
conda activate <ENV_NAME>
```

#### 停用环境
```python
conda deactivate
```

#### 共享环境
> <font style="color:#262626;">与其他人共享您的环境允许他们使用 conda 在他们的计算机上重新创建您的环境。</font>
>
> <font style="color:#262626;">要共享环境及其软件包，您必须将环境的配置导出到</font>`<font style="color:#262626;">.yml</font>`<font style="color:#262626;">文件中。</font>
>

<font style="color:#262626;">共享环境步骤</font>

<font style="color:#262626;">1、激活要导出的环境</font>

```python
# Replace <ENV_NAME> with the name of the environment you want exported
conda activate <ENV_NAME>
```

2、通过运行命令导出环境

```python
conda env export > environment.yml
# 如果当前目录中已有环境配置.yml文件，则该文件将在导出过程中被覆盖。
```

3、<font style="color:#262626;">与其他用户共享导出的环境配置</font>`<font style="color:#262626;">.yml</font>`<font style="color:#262626;">文件。</font>

<font style="color:#262626;">从存储</font>`<font style="color:#262626;">environment.yml</font>`<font style="color:#262626;">文件的目录运行以下命令：</font>

```python
conda env create -f environment.yml
```

<font style="color:#262626;">文件的第一行设置新环境的名称</font>

```yaml
name: stats2  # 设置环境名称
channels:
  - javascript
dependencies:
  - python=3.9
  - bokeh=2.4.2
  - conda-forge::numpy=1.21.*
  - nodejs=16.13.*
  - flask
  - pip
  - pip:
    - Flask-Testing
```

### 配置共享包缓存
> [https://docs.anaconda.com/working-with-conda/packages/shared-pkg-cache/](https://docs.anaconda.com/working-with-conda/packages/shared-pkg-cache/)
>

### 安装conda包
```python
# 安装conda包
conda install package-name

# 安装指定版本的包
conda install package-name=2.3.4

# 仅指定主要版本的包
conda install package-name=2

# 以上命令都是安装到当前活动的环境，该安装到指定的命名环境
conda install package-name=2.3.4 -n some-environment
```

在非联网环境下安装conda包

> [https://docs.anaconda.com/working-with-conda/packages/install-packages/](https://docs.anaconda.com/working-with-conda/packages/install-packages/)
>



