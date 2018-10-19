import random
import re
from datetime import datetime

from flask import request, abort, current_app, make_response, session
from flask import jsonify

from info import redis_store, constants, db
from info.libs.yuntongxun.sms import CCP
from info.models import User
from info.utils.response_code import RET
from . import passport_blu
from info.utils.captcha.captcha import captcha


# 发送图片验证码
@passport_blu.route("/image_code")
def image_code():
    """获取验证码"""
    # 1. 获取请求字符串
    image_code_id = request.args.get("code_id", None)
    if not image_code_id:
        abort(403)

    # 2. 获得验证码，保存
    name, text, image = captcha.generate_captcha()
    current_app.logger.debug("图片验证码内容：{}" .format(text))

    try:
        redis_store.set("image_code_id_" + image_code_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as ret:
        current_app.logger.error(ret)
        abort(500)

    # 3. 将图片返回给客户端
    response = make_response(image)
    # 设置数据类型
    response.headers["Content-Type"] = "image/jpg"
    return response


# 发送验证码
@passport_blu.route("/smscode", methods=["POST"])
def send_sms():
    """验证验证码正确，发送短信"""
    # 1. 接收参数，mobile，image_code, image_code_id
    data = request.json
    mobile = data.get("mobile", None)
    image_code = data.get("image_code", None)
    image_code_id = data.get("image_code_id", None)

    # 2. 判断参数不能为空, 判断参数
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if not re.match(r"1[3456789]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式不正确")

    # 3. 验证redis数据库中验证码是否正确
    try:
        real_image_code = redis_store.get("image_code_id_" + image_code_id)
    except Exception as ret:
        current_app.logger.error(ret)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")

    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg="图片验证码过期")

    # 4. 通过验证后，生成并存储短信验证码，并通过第三方网站向手机号发送验证码

    if image_code.upper() != real_image_code.upper():
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")

    sms_code_str = "%06d" % random.randint(0, 999999)
    current_app.logger.debug("短信验证码内容是：%s" % sms_code_str)
    # 6. 发送短信验证码
    # result = CCP().send_template_sms(mobile, [sms_code_str, constants.SMS_CODE_REDIS_EXPIRES / 5], "1")
    # if result != 0:
    #     # 代表发送不成功
    #     return jsonify(errno=RET.THIRDERR, errmsg="发送短信失败")

    # 保存验证码内容到redis
    try:
        redis_store.set("SMS_" + mobile, sms_code_str, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")

    # 7. 告知发送结果
    return jsonify(errno=RET.OK, errmsg="发送成功")


# 注册
@passport_blu.route("/register", methods=["post"])
def register():
    param_data = request.json
    mobile = param_data.get("mobile", None)
    smscode = param_data.get("smscode", None)
    password = param_data.get("password", None)

    if not all([mobile, smscode, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        if len(smscode) != 6:
            return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
        int_smscode = int(smscode)
    except Exception as ret:
        current_app.logger.error(ret)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 校验手机验证码
    try:
        real_smscode = redis_store.get("SMS_" + mobile)
    except Exception as ret:
        current_app.logger.error(ret)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")

    if not real_smscode:
        return jsonify(errno=RET.DATAERR, errmsg="验证码已过期")

    if int_smscode != int(real_smscode):
        return jsonify(errno=RET.DATAERR, errmsg="验证码错误")

    # 验证成功，生成新用户，以及记录登录状态
    user = User()
    user.mobile = mobile
    user.nick_name= mobile
    user.last_login = datetime.now()
    user.password = password

    # 添加数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as ret:
        db.session.rollback()
        current_app.logger.error(ret)
        return jsonify(errno=RET.DBERR, errmsg="数据保存错误")

    # 记录用户登录状态
    session["user_id"] = user.id
    session["mobile"] = user.mobile
    session["nick_name"] = user.nick_name

    return jsonify(error=RET.OK, errmsg="注册成功")


# 登录
@passport_blu.route("/login", methods=["post"])
def login():
    param_data = request.json
    mobile = param_data.get("mobile", None)
    password = param_data.get("password", None)

    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    # 验证登录成功

    # 添加session

    # 如果没有，则 返回响应报错
    if not re.match(r"1[34789]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="号码输入有误")

        # 3.校验密码是否正确
        # 先验证当前是否有指定手机号的用户
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")

        # 判断用户是否存在
    if not user:
        return jsonify(errno=RET.NODATA, errmsg="用户不存在")

        # 效验登陆的密码和当前的用户的密码是否一致
    if not user.check_password(password):
        return jsonify(errno=RET.PWDERR, errmsg="用户名或者密码错误")

        # 若果在视图函数中，对模型身上的属性有修改，那么需要commit到数据库保存
        # 但是可以不用自己去写，db.session.commit(), 前提是对SQLALchemy有过配置
        # try:
        #     db.session.commit()
        # except Exception as e:
        #     db.session.rollback()
        #     current_app.logger.error(e)

        # 4.保存用户登录的状态
    session["user_id"] = user.id
    session['mobile'] = user.mobile
    session["nick_name"] = user.nick_name

    # 设置当前用户最后一次登录的时间
    user.last_login = datetime.now()

    # 设置sqlalchemy teardown后自动执行一次数据库的提交

    # 5.响应
    return jsonify(errno=RET.OK, errmsg="登陆成功")


# 退出
@passport_blu.route("/logout")
def logout():
    # 删除所有的session
    session.pop("user_id", None)
    session.pop("mobile", None)
    session.pop("nick_name", None)
    return jsonify(errno=RET.OK, errmsg="退出成功")










