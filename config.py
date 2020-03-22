#coding: utf-8
import  os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    # 密钥，用于生成签名或令牌。保护网页表单免受CSRF的恶意攻击
    SECRET_KEY= 'you-will-never-guess'

    #Flask-SQLAlchemy插件从SQLALCHEMY_DATABASE_URI配置变量中获取应用的数据库的位置
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://数据库用户名:用户密码@数据库主机:端口/数据库名?charset=utf8mb4"

    #用于设置数据发生变更之后是否发送信号给应用，若不需要这项功能，因此将其设置为False。
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #添加邮件服务器的信息
    MAIL_SERVER = 'smtp.qq.com'             #邮箱服务器
    MAIL_PORT = 25                          #服务器端口
    MAIL_USE_TLS = 0                        #电子邮件服务器凭证
    MAIL_USERNAME = 'xxx@qq.com'            #发送者邮箱
    MAIL_PASSWORD = 'xxx'                   #发送者邮箱登录密码
    ADMINS = ['xxx@qq.com']                 #接受者邮箱列表

    #分页数据列表长度(每页显示的数据个数)
    POSTS_PER_PAGE = 25

    #支持的语言
    LANGUAGES = ['en','zh','spa', 'jp']

    DEFAULT_BABEL_LOCALE = 'en'         #默认语言

    #用于验证BD翻译服务
    BD_TRANSLATOR_KEY = 'xxx'

