#coding: utf-8
import  os
from redis import Redis

basedir = os.path.abspath(os.path.dirname(__file__))
#***数据库
host = 'localhost'      #数据库地址
port = 3306             #端口
username = 'root'       #用户名
password = 'hua1995225' #密码
charset = 'utf8mb4'
database = 'MicroBlog'  #数据库名

#***app.config***
class Config(object):
    # 密钥，用于生成签名或令牌。保护网页表单免受CSRF的恶意攻击
    SECRET_KEY= 'you-will-never-guess'
    #将session保存在redis中
    SESSION_TYPE = "redis"
    SESSION_REDIS = Redis(host='localhost', port='6379')

    #celery配置
    BROKER_TRANSPORT = 'redis'
    CELERY_BROKER_URL = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
    CELERY_TASK_SERIALIZER = 'pickle'
    CELERY_RESULT_SERIALIZER = 'pickle'
    CELERY_ACCEPT_CONTENT = ['pickle', 'json']

    #Flask-SQLAlchemy插件从SQLALCHEMY_DATABASE_URI配置变量中获取应用的数据库的位置
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://%s:%s@%s:%d/%s?charset=%s" \
                              %(username,password,host,port,database,charset)

    #用于设置数据发生变更之后是否发送信号给应用，若不需要这项功能，因此将其设置为False。
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #添加邮件服务器的信息
    MAIL_SERVER = 'smtp.qq.com'             #邮箱服务器
    MAIL_PORT = 25                          #服务器端口
    MAIL_USE_TLS = 0                        #电子邮件服务器凭证
    MAIL_USERNAME = '****@qq.com'     #发送者邮箱
    MAIL_PASSWORD = '*****'      #发送者邮箱登录密码
    ADMINS = ['******@qq.com']          #接受者邮箱列表

    #分页数据列表长度(每页显示的数据个数)
    POSTS_PER_PAGE = 20

    #支持的语言
    LANGUAGES = ['en','zh','es']

    DEFAULT_BABEL_LOCALE = 'en'         #默认语言

    #用于验证BD翻译服务
    BD_TRANSLATOR_KEY = '*****'



#文本标注
table = 'Test'   #表名
data_name = 'review'    #要标注的文本列的名称
#标定的标签,及标签类型
lable = ('leval', 'int')

if __name__ == '__main__':
    config = Config()
    print(config.SQLALCHEMY_DATABASE_URI)





