#coding: utf-8
from flask import render_template, request
from webapp import app, db


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'),404

# 数据库错误
@app.errorhandler(500)
def interal_error(error):
    db.session.rollback()       #执行会话回滚来将会话重置为干净的状态
    return render_template('500.html'),500


#访问频次过高
@app.errorhandler(429)
def limiter_error(error):
    table_name = request.args['table_name']
    return render_template('429.html',table_name=table_name),429