from flask import Blueprint

# 创建蓝图
passport_blu = Blueprint("passport", __name__, url_prefix="/passport")

# 将视图函数全部导入
from . import views
