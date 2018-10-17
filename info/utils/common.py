# 一些简单的通用的全局公用方法，eg: 过滤器， g变量
from functools import wraps

from flask import session, current_app, g

from info.models import User


# 用户的登录状态存储从session中取出放入g变量中

def user_login_data(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id", None)
        user = None

        if user_id:
            try:
                user = User.query.get(user_id)
            except Exception as ret:
                current_app.logger.error(ret)
        # 将user赋值给g变量
        g.user = user
        return f(*args, **kwargs)

    return wrapper
