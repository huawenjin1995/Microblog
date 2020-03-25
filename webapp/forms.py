#coding: utf-8
#***定义表单类***

from flask_wtf import FlaskForm
from wtforms import StringField , PasswordField, BooleanField, SubmitField, TextAreaField, RadioField, IntegerField      #表单字段的类
from wtforms.validators import DataRequired, ValidationError,Email, EqualTo, Length, NumberRange
from webapp.models import User
#字段中的可选参数validators用于验证字段是否符合预期,DataRequired验证器仅验证字段输入是否为空
from flask_babel import _, lazy_gettext as _l
from config import lable


#***用户登录表单***
class LoginForm(FlaskForm):
    #用户登录表单,每个字段类都接受一个描述或别名作为第一个参数，
    #并生成一个实例来作为LoginForm的类属性。
    username = StringField(_l('Username'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign in'))


#***用户注册表单***
class RegistrationForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Repeat Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Register'))

#**添加usermame和email验证器**
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_('Please use a different username.'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_('Please use a different email address.'))


#***用户个人资料表单***
class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'), validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_('Please use a different username.'))


#***用户动态表单***
class PostForm(FlaskForm):
    post = TextAreaField(_l('Say something'), validators=[DataRequired(),
                        Length(min=1, max= 140)])
    submit = SubmitField(_l('Submit'))


#***请求重置密码表单***
class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Request Password Reset'))


#***重置密码表单***
class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Repeat Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Request Password Reset'))


#***请求标注数据***
class DataLabelRequestForm(FlaskForm):
    table_name = StringField(_l('Select Data'), validators=[DataRequired(), ])
    submit = SubmitField(_l('Submit'))



#***数据标注***
class DataLabelForm(FlaskForm):
    #根据客户要求制作标签
    leval = IntegerField(_l('leval'),validators=[DataRequired(),
                        NumberRange(1,3)],description='评价（3:好，2：中等，1：差）')
    cost_perform = IntegerField(_l('cost_perform'),validators=[DataRequired(),
                        NumberRange(1,3)],description='性价比（3:好，2：中等，1：差）')
    appearance = IntegerField(_l('appearance'),validators=[DataRequired(),
                        NumberRange(1,3)],description='外观（3:好，2：中等，1：差）')
    applicability = IntegerField(_l('applicability'),validators=[DataRequired(),
                        NumberRange(1,3)],description='使用性（3:好，2：中等，1：差）')
    submit = SubmitField(_l('Submit'))




