from flask import render_template, g, current_app, jsonify, abort, request

from info import constants, db
from info.models import News, Comment, User, CommentLike
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

    # 显示新闻评论
    comments = []
    try:
        comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)

    comment_like_ids = []
    if g.user:
        try:
            # 需求：查询当前用户在当前新闻里面都点赞了哪些评论
            # 1. 查询出当前新闻的所有评论 ([COMMENT]) 取到所有的评论id  [1, 2, 3, 4, 5]
            comment_ids = [comment.id for comment in comments]
            # 2. 再查询当前评论中哪些评论被当前用户所点赞 （[CommentLike]）查询comment_id 在第1步的评论id列表内的所有数据 & CommentList.user_id = g.user.id
            comment_likes = CommentLike.query.filter(CommentLike.comment_id.in_(comment_ids),
                                                     CommentLike.user_id == g.user.id).all()
            # 3. 取到所有被点赞的评论id 第2步查询出来是一个 [CommentLike] --> [3, 5]
            comment_like_ids = [comment_like.comment_id for comment_like in comment_likes]  # [3, 5]
        except Exception as e:
            current_app.logger.error(e)

    comment_dict_li = []
    for comment in comments:
        comment_dict = comment.to_dict()
        # 代表没有点赞
        comment_dict["is_like"] = False
        # 判断当前遍历到的评论是否被当前登录用户所点赞
        if comment.id in comment_like_ids:
            comment_dict["is_like"] = True
        comment_dict_li.append(comment_dict)

    data = {
        "user": user,
        "news_detail": news_detail.to_dict() if news_detail else None,
        "rank_news": news_dict_li if news_dict_li else None,
        "is_collected": is_collected,
        "comments": comment_dict_li,
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


# 评论
@news_blu.route("/news_comment", methods=["post"])
@user_login_data
def news_comment():
    """评论"""
    # 1. 获取新闻id，评论，父级评论id
    # 2. 校验
    # 3. 获取新闻对象
    # 4. 创建评论对象
    # 5. 提交sql事务，返回评论字典至前端
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    # 1. 取到请求参数
    news_id = request.json.get("news_id")
    comment_content = request.json.get("comment")
    parent_id = request.json.get("parent_id")

    # 2. 判断参数
    if not all([news_id, comment_content]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        news_id = int(news_id)
        if parent_id:
            parent_id = int(parent_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 查询新闻，并判断新闻是否存在
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="未查询到新闻数据")

    # 3. 初始化一个评论模型，并且赋值
    comment = Comment()
    comment.user_id = user.id
    comment.news_id = news_id
    comment.content = comment_content
    if parent_id:
        comment.parent_id = parent_id

    # 添加到数据库
    # 为什么要自己去commit()?，因为在return的时候需要用到 comment 的 id
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()

    return jsonify(errno=RET.OK, errmsg="OK", data=comment.to_dict())
    
