from flask import current_app, render_template, g, request, jsonify

from info.models import News, Category
from info.utils.common import user_login_data
from info.utils.response_code import RET
from . import index_blu
from info import constants


@index_blu.route("/news_list")
def news_list():
    # 1. 获取数据
    cid = request.args.get("cid", "1")
    page = request.args.get("page", "1")
    per_page = request.args.get("per_page", "10")

    # 1.1 验证请求参数
    try:
        page = int(page)
        cid = int(cid)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 2. 查询数据库，获得新闻字典
    filter_list = []
    if cid != 1:
        filter_list.append(News.category_id == cid)

    paginate = News.query.filter(*filter_list).order_by(News.create_time.desc()).paginate(page=page, per_page=per_page,
                                                                                          error_out=False)

    current_page = paginate.page
    total_pages = paginate.pages
    news_model_list = paginate.items

    news_dict_list = [news.to_basic_dict() for news in news_model_list]

    # 3. 返回
    data = {
        "current_page": current_page,
        "total_page": total_pages,
        "news_dict_li": news_dict_list,
    }

    return jsonify(errno=RET.OK, errmsg="查询成功", data=data)


@index_blu.route('/')
@user_login_data
def index():
    # 获取g变量中的user
    user = g.user

    # 展示新闻分类
    categories = Category.query.all()

    category_li = []
    for category in categories:
        category_li.append(category.to_dict())

    # 完成新闻排行
    # 1. 查询新闻，点击率排序
    news_object_li = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)

    # 2. 返回对象列表，获取新闻字典，写入字典,返回
    news_dict_li = [news_object.to_basic_dict() if news_object else None for news_object in news_object_li]

    data = {
        "user": user.to_dict() if user else None,
        "rank_news": news_dict_li if news_dict_li else None,
        "category_li": category_li,
    }

    return render_template("news/index.html", data=data)


@index_blu.route("/favicon.ico")
def favicon():
    print(current_app.url_map)
    return current_app.send_static_file("news/favicon.ico")
