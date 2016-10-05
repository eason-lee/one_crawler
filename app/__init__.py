# -*- coding: utf-8 -*-

from flask import Flask
import time
from pymongo import MongoClient


# 把 flask 的初始化放到函数中
# 由外部启动函数来调用
#
def init_app():
    # 初始化并配置 flask
    app = Flask(__name__)
    # 这一行 加了就没 warning
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    # 设置你的加密 key
    app.secret_key = 'TODO fixme'
    # 初始化 db
    client = MongoClient()
    db = client.ones
    collection = db.one

    # 必须在函数中 import 蓝图
    # 否则循环引用(因为蓝图中 import 了 model, model 引用了这个文件里面目的 db)
    from .controllers import main as controllers
    # from .api import main as api

    # 注册蓝图
    app.register_blueprint(controllers)
    # app.register_blueprint(api, url_prefix='/api')
    # 把 app 引用返回
    return app
