#coding: utf-8
from flask import render_template, flash, redirect, url_for, request, g, jsonify, session
from webapp import app, db, limiter
from webapp.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm,\
    ResetPasswordRequestForm, ResetPasswordForm, DataLabelRequestForm, DataLabelForm, TrainlabelForm
from flask_login import current_user, login_user, logout_user, login_required
from webapp.models import User, Post
from werkzeug.urls import url_parse
from flask_babel import _, get_locale
from datetime import datetime
from webapp.myemail import send_password_reset_email
from guess_language import guess_language
from webapp.translate import translate
import config, time
from data_label.populate_label_data import db_label
from data_label.server_label_db import  write_form, predict_labels, train_datas
from webapp.listPagination import ListPagination


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        language = guess_language(form.post.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        post = Post(body=form.post.data, author=current_user, language=language)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('index'))
    #分页
    page = request.args.get('page',1, type=int)
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False
    )
    next_url = url_for('index', page=posts.next_num if posts.has_next else None)
    prev_url = url_for('index', page = posts.prev_num if posts.has_prev else None)
    return render_template('index.html', title=_('Home'),form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)
    #posts.items返回查询结果列表, posts.prev_num上一页的页码


#***用户登录***
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:       #检查用户是否已经登录
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        #form.validate_on_submit()实例方法会执行form校验的工作。
        # 当浏览器发起GET请求的时候，它返回False
        #当用户在浏览器点击提交按钮后，浏览器会发送POST请求。
        # form.validate_on_submit()就会获取到所有的数据，运行字段各自的验证器，
        # 全部通过之后就会返回True，这表示数据有效
        # flash('Login requested for user {}, remember_me={}'.format(
        #     form.username.data, form.remember_me.data))
        # return redirect(url_for('index'))

        user = User.query.filter_by(username=form.username.data).first()
        #filter_by()的结果是一个只包含具有匹配用户名的对象的查询结果集,当你只需要一个结果时，
        #通常使用first()方法
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)
        #将用户登录状态注册为已登录，这意味着用户导航到任何未来的页面时，
        #应用都会将用户实例赋值给current_user变量。

        next_page = request.args.get('next')
        #实现登录成功之后自定重定向回到用户之前想要访问的页面
        #当一个没有登录的用户访问被@login_required装饰器保护的视图函数时，
        #装饰器将重定向到登录页面，不过，它将在这个重定向中包含一些额外的信息以便登录后的回转

        if not next_page or url_parse(next_page).netloc!='':
        #攻击者可以在next参数中插入一个指向恶意站点的URL，因此应用仅在重定向URL是相对路径时
        #才执行重定向，这可确保重定向与应用保持在同一站点中。 为了确定URL是相对的还是绝对的，
        #我使用Werkzeug的url_parse()函数解析，然后检查netloc属性是否被设置。
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title=_('Sign In'), form=form)


#***用户注销(登出）***
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


#***用户注册***
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations, you are now a registered user!'))
        return redirect(url_for('login'))
    return render_template('register.html', title=('Register'), form=form)


#***个人主页***
@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username= username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


#更新用户最后访问时间
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())



#***修改用户个人资料***
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'),
                           form=form)


#***用户关注***
@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('index'))
    if user == current_user:
        flash(_('You cannot follow yourself!'))
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(_('You are following %(username)s!',username=username))
    return redirect(url_for('user', username=username))


#***用户取消关注***
@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.',username=username))
        return redirect(url_for('index'))
    if user == current_user:
        flash(_('You cannot unfollow yourself!'))
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following %(username)s.',username=username))
    return redirect(url_for('user', username=username))


#***‘发现’页面，展示所有用户的全部动态
@app.route('/explore')
@login_required
def explore():
    #分页
    page = request.args.get('page',1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False
    )
    next_url = url_for('explore',page=posts.next_num if posts.has_next else None)
    prev_url = url_for('explore',page=posts.prev_num if posts.has_prev else None)
    return render_template('index.html', title=_('Explore'), posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


#***重置密码请求***
@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(_('Check your email for the instructions to reset your password'))
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title=_('Reset Password'), form=form)


#***重置密码***
@app.route('/reset_password<token>', methods=['GET','POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


#***文本翻译***
@app.route('/translate', methods=['POST'])
@login_required
def translate_text():
    # des_language = request.form['dest_language']
    # if des_language == 'es_ES':     #西班牙语
    #     des_language = 'spa'
    # return (request.form['dest_language'])
    return jsonify({'text':translate(request.form['text'],
                                     request.form['source_language'],
                                     request.form['dest_language'])})


#判断有没有待标注的数据，有：返回True
def is_data_to_label(table):
    unlabeled_data = db_label.get_one_unlabeled(table=table)
    if unlabeled_data:      # 有未标记的
        return True
    else:
        return False

#***选择需要标注的数据***
@app.route('/request_label', methods=['GET', 'POST'])
@login_required
def request_label():
    form = DataLabelRequestForm()
    client_db_table = config.table
    # client_db_table = 'Test'

    if form.validate_on_submit():
        if form.table_name.data != client_db_table:     #输入的数据表名错误
            flash(_('Please Select Valid Data!'))
            return redirect(url_for('request_label'))
        return redirect(url_for('data_label',table_name=client_db_table))
    if request.method == 'GET':
        if is_data_to_label(table=client_db_table):                          #有数据未标注
            return render_template('request_label.html',table_name=client_db_table, form=form)
        #无数据标注
        return redirect(url_for('data_label',table_name=client_db_table))


#***数据标注***
@app.route('/data_label', methods=['GET', 'POST'])
@login_required
def data_label():
    form = DataLabelForm()
    if 'table_name' not in request.args or not request.args['table_name']:
        return redirect(url_for('request_label'))
    table_name = request.args['table_name']
    unlabeled_data = db_label.get_one_unlabeled(table=table_name)                 #获取未标注的记录(id,text)

    if not unlabeled_data:
        flash('All data is labeled! Train the labeled data')
        return render_template('data_label.html',table_name=table_name)
    #未标注的数据的id,和文本
    id = unlabeled_data[0][0]
    text = unlabeled_data[1]

    if form.validate_on_submit():                      #有效提交，开始读写数据库
        #更新记录
        label = form.level.data[0]
        db_label.update_one_label(id=id,label=label, username=current_user.username,
                                  table=table_name)
        return redirect(url_for('data_label',table_name=table_name))

    label = db_label.get_one_data(id=id,table=table_name, column='label')
    # return str(label[0])
    if label:
        write_form(label=label, form=form)  # 写表单
    return render_template('data_label.html', form=form,text=text,table_name=table_name)


#***预测标签***
@app.route('/predict_label', methods=['GET','POST'])
@limiter.limit("2 per minute")                          #限制每分钟访问次数
@login_required
def predict_label():
    if request.method == 'GET':
        if 'table_name' not in request.args or not request.args['table_name']:
            return redirect(url_for('request_label'))
        table_name = request.args['table_name']
        return render_template('predict_label.html', table_name=table_name)

    if request.method == 'POST':
        table_name = config.table
        task = predict_labels.delay(table=table_name)       #开始预测
        return jsonify({}), 202, {'Location': url_for('predict_taskstatus',
                                                      task_id=task.id)}

#***预测任务进度***
@app.route('/predict_taskstatus/<task_id>')
def predict_taskstatus(task_id):
    task = predict_labels.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }

    if task.state == 'SUCCESS':
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': 'SUCCESS...'
        }

    elif task.state == 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
        return jsonify(response)
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)


#***训练数据***
@app.route('/train_label_data', methods=['GET','POST'])
@limiter.limit("2 per minute")                          #限制每分钟访问一次
@login_required
def train_label_data():
    if request.method == 'GET':
        if 'table_name' not in request.args or not request.args['table_name']:
            return redirect(url_for('request_label'))
        table_name = request.args['table_name']
        return render_template('train_label.html', table_name=table_name)
    if request.method == 'POST':
        table_name = config.table
        session['train_flag'] = 1 if session.get('train_flag') != 1 else 0      #交替训练
        task = train_datas.delay(flag=session['train_flag'],table=table_name)   #训练数据
        return jsonify({}), 202, {'Location': url_for('train_taskstatus',
                                                      task_id=task.id)}

#***训练任务进度***
@app.route('/train_taskstatus/<task_id>')
def train_taskstatus(task_id):
    task = train_datas.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }

    if task.state == 'SUCCESS':
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': 'SUCCESS...'
        }

    elif task.state == 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
        return jsonify(response)
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)



#***修改预测标签与实际标签不符的数据***
@app.route('/reset_data_label', methods=['GET', 'POST'])
@limiter.limit("3 per minute")
@login_required
def reset_data_label():
    form = DataLabelForm()
    table_name = request.args['table_name']
    dif_id = db_label.get_diff_predict(username=current_user.username,table=table_name)
    if dif_id:
        # 分页
        page = request.args.get('page', 1, type=int)
        data = ListPagination(dif_id,page=page)
        next_url = url_for('reset_data_label', table_name=table_name, source_id=data.items, page=data.next_num) \
            if data.has_next else None
        prev_url = url_for('reset_data_label', table_name=table_name, source_id=data.items, page=data.prev_num) \
            if data.has_prev else None

        if 'id' in request.args and request.args['id']:
            id = int(request.args['id'])
            text = db_label.get_one_data(id=id,table=table_name)
            #用数据库中原来标注信息回填form
            label = db_label.get_one_data(id=id, table=table_name,column='label')
            # return str(label[0])
            write_form(label=label,form=form)                       #写表单

            return render_template('reset_data_label.html', table_name=table_name,
                                   source_id=data.items,text=text,form=form,page=page,
                                   next_url=next_url,prev_url=prev_url)

        if form.validate_on_submit():  # 有效提交，开始读写数据库
            id = int(request.args['id'])
            db_label.update_one_label(id=id,form=form,username=current_user.username,
                                      table=table_name)             #更改label
            return redirect(url_for('reset_data_label', table_name=table_name))

        return render_template('reset_data_label.html', table_name=table_name,
                               source_id=data.items,page=page, next_url=next_url,
                               prev_url=prev_url)
    else:
        flash('You have no data to relabeled')
        return redirect(url_for('index'))

