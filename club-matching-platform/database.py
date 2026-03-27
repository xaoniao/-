"""
数据库初始化配置
"""
from flask import Flask
from models import db
import os


def create_app():
    """创建 Flask 应用"""
    app = Flask(__name__)

    # 配置数据库
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///club_platform.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'club-matching-platform-secret-key'

    # 初始化数据库
    db.init_app(app)

    # 创建数据库表
    with app.app_context():
        db.create_all()

    return app


def init_db():
    """初始化数据库"""
    app = create_app()
    with app.app_context():
        db.create_all()
        print("数据库初始化完成！")


if __name__ == '__main__':
    init_db()
