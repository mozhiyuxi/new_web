# 完成flask业务逻辑
import logging
from logging.handlers import RotatingFileHandler
from flask.ext.wtf.csrf import CSRFProtect
from flask_session import Session
from flask.ext.sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask import Flask

from config import config

# 1. 完成日志函数定义

# 2. 第一app函数，生成app，将配置类传入app中

# 设置变量类型, 将redis_store设置为全局变量
redis_store = None  # type: StrictRedis
db = SQLAlchemy()


def setup_log(config_name):
    # 设置日志的记录等级
    logging.basicConfig(level=config[config_name].LOG_LEVEL)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/logs", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def create_app(config_name):
    setup_log(config_name)
    # 创建Flask对象
    app = Flask(__name__)
    # 加载配置
    app.config.from_object(config[config_name])
    # 通过app初始化
    db.init_app(app)
    # 初始化 redis 存储对象
    global redis_store
    redis_store = StrictRedis(host=config[config_name].REDIS_HOST, port=config[config_name].REDIS_PORT,
                              decode_responses=True)

    # 开启csrf验证
    CSRFProtect(app)
    # 设置session保存指定位置
    Session(app)

    # 导入蓝图
    from info.modules.index import index_blu
    app.register_blueprint(index_blu)

    return app
