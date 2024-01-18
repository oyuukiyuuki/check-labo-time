from check_time import db
from check_time.models import User, CheckTime
from check_time.users.forms import LoginForm, RegistrationForm, UpdataUserForm
from flask_login import current_user, login_required, login_user, logout_user
from flask_cors import cross_origin
from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    Flask,
    jsonify,
    request,
)
from datetime import datetime
from pytz import timezone
import time
from wtforms import ValidationError

device = Blueprint("device", __name__)

# テスト用
# @device.route("/registform")
# def show_form():
#     return render_template("users/register.html")


@device.route("/api/signup", methods=["POST"])
@cross_origin(origins=["http://127.0.0.1:5500"], methods=["POST"])
def signup():
    error_flag = False
    user_data = request.get_json()
    message = ""
    if User.query.filter_by(username=user_data["username"]).first():
        error_flag = True
        message = "入力されたユーザ名はすでに使われてます\n"
    if User.query.filter_by(email=user_data["email"]).first():
        error_flag = True
        message += "入力されたメールアドレスはすでに使われてます\n"
    if User.query.filter_by(nfc_id=user_data["nfc_id"]).first():
        error_flag = True
        message += "入力されたタグはすでに使われています\n"
    if error_flag:
        response = {"message": message}
        return response, 400
    if user_data:
        user = User(
            email=user_data["email"],
            username=user_data["username"],
            password=user_data["password"],
            administrator="0",
            grade=user_data["grade"],
            nfc_id=user_data["nfc_id"],
        )
        db.session.add(user)
        db.session.commit()
        response = {"message": "ユーザ登録が完了しました"}
        return response, 200
    else:
        response = {"message": "ユーザ登録に失敗しました"}
        return response, 400


@device.route("/api/regist_time", methods=["POST"])
@cross_origin(origins=["http://127.0.0.1:5500"], methods=["POST"])
def regist_time():
    print("aaa")
    time_data = request.get_json()
    print(time_data["nfc_id"])
    user = User.query.filter_by(nfc_id=time_data["nfc_id"]).first()
    print(user)
    check_time = (
        CheckTime.query.filter_by(user_id=user.id).order_by(CheckTime.id.desc()).first()
    )
    if check_time is None:
        in_time = CheckTime(
            user_id=user.id,
            in_time=datetime.now(timezone("Asia/Tokyo")),
        )
        db.session.add(in_time)
        db.session.commit()
        response = {"message": "頑張ってください"}
        return response, 200
    else:
        if time_data["status"] > 0:
            if check_time.out_time is None:
                check_time.out_time = datetime.now(timezone("Asia/Tokyo"))
                check_time.status = time_data["status"]
                db.session.add(check_time)
                db.session.commit()
                response = {"message": "お疲れ様です"}
                return response, 200
            else:
                response = {"message": "入室情報がありません"}
                return response, 400
        else:
            if check_time.out_time is None:
                response = {"message": "前回の退室時間が記録されていません"}
                return response, 400
            else:
                in_time = CheckTime(
                    user_id=user.id,
                    in_time=datetime.now(timezone("Asia/Tokyo")),
                )
                db.session.add(in_time)
                db.session.commit()
                response = {"message": "頑張ってください"}
                return response, 200
