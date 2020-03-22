#coding: utf-8
#***发送电子邮件***

from flask_mail import Message, Mail
from webapp import app
from flask import render_template
from threading import Thread
from flask_babel import _

#***创建邮件实例***
mail = Mail(app)

#该函数运行在后台线程中
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)
#mail.send()方法需要访问电子邮件服务器的配置值,而这必须通过访问应用属性的方式来
#实现with app.app_context()调用创建的应用上下文使得应用实例可以通过
#来自Flask的current_app变量来进行访问。


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email(_('[Microblog] Reset Your Password'),
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))