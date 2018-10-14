from . import index_blu
from flask import current_app


@index_blu.route('/')
def demo1():
    current_app.logger.error("error测试")
    return "蓝图测试"
