#coding: utf-8
import jwt
from datetime import datetime
from time import time
from webapp import db, app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin   #在用户模型上实现某些属性和方法
from webapp import login
from hashlib import md5


#***followers关联表***
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)




#***构建User表***
# User类继承自db.Model，它是Flask-SQLAlchemy中所有模型的基类。
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    #User类有一个新的posts字段，用db.relationship初始化。这不是实际的数据库字段，
    #而是用户和其动态之间关系的高级视图，因此它不在数据库图表中。对于一对多关系，
    #db.relationship字段通常在“一”的这边定义，并用作访问“多”的便捷方式。因此，
    #如果我有一个用户实例u，表达式u.posts将运行一个数据库查询，返回该用户发表过的所有动态。
    #db.relationship的第一个参数表示代表关系“多”的类。 backref参数定义了代表“多”的
    #类的实例反向调用“一”的时候的属性名称。这将会为用户动态添加一个属性post.author，
    #调用它将返回给该用户动态的用户实例。 lazy参数定义了这种关系调用的数据库查询是如何执行的，
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)    #世界标准时间

    #关联粉丝表
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    #__repr__方法用于在调试时打印用户实例
    def __repr__(self):
        return '<User {}>'.format(self.username)

    #存储hash_password
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    #验证用户密码
    def check_password(self,password):
        return check_password_hash(self.password_hash, password)

    #生成用户图像, size为图像的像素大小
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    #添加关注
    def follow(self,user):
        if not self.is_following(user):
            self.followed.append(user)

    #删除关注
    def unfollow(self,user):
        if self.is_following(user):
            self.followed.remove(user)

    #判断是否关注
    def is_following(self,user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    #展示该用户自己的动态以及他/她关注的其他用户的动态
    def followed_posts(self):
        # 关注的其他人的动态
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id = self.id)       #用户自己的动态
        #合并动态，最新的动态排在最前
        return followed.union(own).order_by(Post.timestamp.desc())
        #返回的是flask_sqlalchemy.BaseQuery对象，用方法.all()可以得到一个列表

    #生成令牌
    def get_reset_password_token(self, expires_in=600):     #过期时间600s
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    #验证令牌
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


#***构建Post表, 表示用户发表的动态***
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    #请注意，在utcnow之后没有包含()，所以传递函数本身，而不是调用它的结果）
    #通常，在服务应用中使用UTC日期和时间是推荐做法。 这可以确保你使用统一的时间戳，
    #无论用户位于何处，这些时间戳会在显示时转换为用户的当地时间。

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    #user_id字段被初始化为user.id的外键，这意味着它引用了来自用户表的id值。
    #本处的user是数据库表的名称，Flask-SQLAlchemy自动设置类名为小写来
    #作为对应表的名称
    language = db.Column(db.String(5))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


#使用Flask-Login的@login.user_loader装饰器来为用户加载功能注册函数。
#Flask-Login将字符串类型的参数id传入用户加载函数，因此使用数字ID的数据
#库需要如上所示地将字符串转换为整数。
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

