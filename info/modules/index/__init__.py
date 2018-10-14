from flask import Blueprint

# 创建蓝图
index_blu = Blueprint("index", __name__)

# 将视图函数全部导入
from . import views
