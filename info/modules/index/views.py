from . import index_blu
from flask import current_app, render_template


@index_blu.route('/')
def demo1():
    current_app.logger.error("error测试")
    return render_template("news/index.html")
