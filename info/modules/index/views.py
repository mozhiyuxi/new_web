from info.utils.common import user_login_data
from . import index_blu
from flask import current_app, render_template, g


@index_blu.route('/')
@user_login_data
def index():
    user = g.user
    data = {
        "user": user.to_dict() if user else None,
    }

    return render_template("news/index.html", data=data)


@index_blu.route("/favicon.ico")
def favicon():
    print(current_app.url_map)
    return current_app.send_static_file("news/favicon.ico")
