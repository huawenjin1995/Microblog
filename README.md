# README

## 安装依赖包

1. 进入项目所在目录, 安装venv(若已存在，跳过): "pip3 install venv"

2. 激活venv: "source  venv/bin/activate" , 激活成功后工作目录样式：

   "(venv) $"

3. 安装flask: "pip3 install flask"

4. 安装剩下项目中需要的flask插件,注意! 注意！注意！，类似：  "flask_sqlalchemy" 在安装过程中需要改为 "flask-sqlalchemy"

   

##  设置环境变量,运行flask

1. "export FLASK_APP=microblog"
2. flask 默认为生产环境，可设置开发模式："export FLASK_ENV=development"
3. 开启degug模式: "export FLASK_DEBUG=1"
4. 运行："flask run"



## 数据库迁移,更新

1. "flak db init"
2. "flask db migrate", 后续数据库的表发生改变时，需要运行此命令
3. "flask db upgrade", 后续数据库的表发生改变时，需要运行此命令



## 翻译包

```
运行flask --help将列出translate命令作为选项。 flask translate --help将显示我定义的三个子命令：

(venv) $ flask translate --help
Usage: flask translate [OPTIONS] COMMAND [ARGS]...

  Translation and localization commands.

Options:
  --help  Show this message and exit.

Commands:
  compile  Compile all languages.
  init     Initialize a new language.
  update   Update all languages.
所以现在工作流程就简便多了，而且不需要记住长而复杂的命令。 要添加新的语言，请使用：

(venv) $ flask translate init <language-code>
在更改_()和_l()语言标记后更新所有语言：

(venv) $ flask translate update
在更新翻译文件后编译所有语言：

(venv) $ flask translate compile
```



### 新增文本标注功能

1. 该模块对应 data_label
2. 需要安装celery和redis : 将文本预测和文本训练放在celery 的worker

运行，redis作为消息代理

​	3.运行flask前需启动redis和celery，运行redis命令: "redis-server"

运行celery命令: "celery worker -A microblog.celery --loglevel=info"



###  新增根据访问者的IP限制其访问频率，频次

-  利用flask_limiter实现对访问者的访问频次进行限制，特别是与数据库相关的路由需要加以限制，以免频繁对数据库操作导致数据库崩溃。

