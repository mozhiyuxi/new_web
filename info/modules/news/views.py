from flask import render_template, g, current_app, jsonify, abort, request

from info import constants, db
from info.models import News
from info.utils.common import user_login_data
from info.utils.response_code import RET
from . import news_blu


# 新闻详情页
@news_blu.route("/<int:news_id>")
@user_login_data
def detail(news_id):
    # 默认未收藏
    is_collected = False
    user = g.user

    news_object_li = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    news_dict_li = [news_object.to_basic_dict() if news_object else None for news_object in news_object_li]

    # 1. 获取参数，路由获取新闻id,并校验
    news_id = int(news_id)

    # 2. 查询sql，返回新闻详情
    news_detail = None
    try:
        news_detail = News.query.get(news_id)
    except Exception as ret:
        current_app.logger.error(ret)
        abort(404)

    if not news_detail:
        # 返回数据未找到的页面
        abort(404)

    if user:
        try:
            if news_detail in user.collection_news:
                is_collected = True
        except Exception as ret:
            current_app.logger.error(ret)

    # 点击量加一
    news_detail.clicks += 1

    data = {
        "user": user,
        "news_detail": news_detail.to_dict() if news_detail else None,
        "rank_news": news_dict_li if news_dict_li else None,
        "is_collected": is_collected
    }
    return render_template("news/detail.html", data=data)


# 收藏
@news_blu.route("/news_collect", methods=["post"])
@user_login_data
def news_collect():

    """新闻收藏"""

    user = g.user
    json_data = request.json
    news_id = json_data.get("news_id")
    action = json_data.get("action")

    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    if not news_id:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if action not in ("collect", "cancel_collect"):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="新闻数据不存在")

    if action == "collect":
        if news not in user.collection_news:
            user.collection_news.append(news)
    else:
        if news in user.collection_news:
            user.collection_news.remove(news)

    # try:
    #     db.session.commit()
    # except Exception as e:
    #     current_app.logger.error(e)
    #     db.session.rollback()
    #     return jsonify(errno=RET.DBERR, errmsg="保存失败")
    return jsonify(errno=RET.OK, errmsg="操作成功")
