#coding=utf-8
#创建应用实例,初始化插件
import logging, os
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from logging.handlers import SMTPHandler
from logging.handlers import RotatingFileHandler
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l


app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)                #数据库

login = LoginManager(app)           #管理用户登录
@login.user_loader
def load_user(user_id):
	return None


login.login_view = 'login'
#强制用户在查看应用的特定页面之前登录,上面的'login'值是登录视图函数（endpoint）名
login.login_message = _l('Please login to access this page')

#migrate数据库迁移引擎,通过运行  'flask db init' 来创建迁移存储库,
#'flask db migrate' 子命令生成这些自动迁移：flask db migrate命令
# 不会对数据库进行任何更改，只会生成迁移脚本。 要将更改应用到数据库，
# 必须使用flask db upgrade命令。降级使用 flask db downgrade 命令
migrate = Migrate(app, db)



# print(app.config['SECRET_KEY'])
# print(app.config['SQLALCHEMY_DATABASE_URI'])current_user.username
# print(app.debug)

#***添加Flask-Bootstrap插件***
bootstrap = Bootstrap(app)


#***添加Flask-Moment插件，用于日期和时间转换
moment = Moment(app)


#***添加Flask-Babel插件，用于简化翻译工作
babel = Babel(app)

#选择最匹配的语言
@babel.localeselector
def get_locale():
    # return request.accept_languages.best_match(app.config['LANGUAGES'])
    return 'en'




#****通过邮件发送错误***
if not app.debug:
    #为Flask的日志对象添加一个SMTPHandler的实例：
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr= app.config['MAIL_USERNAME'],
            toaddrs=app.config['ADMINS'],
            subject='Microblog Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)



    #启用另一个基于文件类型RotatingFileHandler的日志记录器
    if not os.path.exists('logs'):
        os.mkdir('logs')
        #日志文件的存储路径位于顶级目录下，相对路径为logs/microblog.log，
        #如果其不存在，则会创建它。
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240,
                                       backupCount=10)
    #日志文件大小限制为10k，保留最后10个日志文件作为备份
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    #设置日志消息格式，依次为：时间戳、日志记录级别、消息以及日志来源的源代码文件和行号。
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog startup')

from webapp import routes, models, errors
