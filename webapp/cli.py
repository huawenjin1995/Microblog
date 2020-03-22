#coding: utf-8
#***翻译命令组***
import os
from webapp import app
import click

@app.cli.group()
def translate():
    '''ranslation and localization commands.'''
    pass

@translate.command()
@click.argument('lang')
def init(lang):
    """Initialize a new language."""
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
        raise RuntimeError('extract command failed')
    if os.system(
            'pybabel init -i messages.pot -d webapp/translations -l ' + lang):
        raise RuntimeError('init command failed')
    os.remove('messages.pot')


@translate.command()
def update():
    """Update all languages."""
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
        raise RuntimeError('extract command failed')
    if os.system('pybabel update -i messages.pot -d webapp/translations'):
        raise RuntimeError('update command failed')
    os.remove('messages.pot')


@translate.command()
def compile():
    """Compile all languages."""
    if os.system('pybabel compile -d webapp/translations'):
        raise RuntimeError('compile command failed')


#************************************
#此时，运行flask --help将列出translate命令作为选项。 flask translate --help将显示我定义的三个子命令：
#
# (venv) $ flask translate --help
# Usage: flask translate [OPTIONS] COMMAND [ARGS]...
#
#   Translation and localization commands.
#
# Options:
#   --help  Show this message and exit.
#
# Commands:
#   compile  Compile all languages.
#   init     Initialize a new language.
#   update   Update all languages.
# 所以现在工作流程就简便多了，而且不需要记住长而复杂的命令。 要添加新的语言，请使用：
#
# (venv) $ flask translate init <language-code>
# 在更改_()和_l()语言标记后更新所有语言：
#
# (venv) $ flask translate update
# 在更新翻译文件后编译所有语言：
#
# (venv) $ flask translate compile
