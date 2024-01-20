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
    make_response,
)
from datetime import datetime
from pytz import timezone
import time
from wtforms import ValidationError
from flask_jwt_extended import (
    jwt_required,
    create_access_token,
    JWTManager,
    get_jwt_identity,
)


device = Blueprint("device", __name__)


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
        token = create_access_token(identity=user_data["email"])
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
        response = {"message": "ユーザ登録が完了しました", "token": token, "user_id": user.id}
        return response, 200
    else:
        response = {"message": "ユーザ登録に失敗しました"}
        return response, 400


@device.route("/api/login", methods=["POST"])
@cross_origin(origins=["http://127.0.0.1:5500"], methods=["POST"])
def login():
    user_data = request.get_json()
    print(user_data)
    user = User.query.filter_by(email=user_data["email"]).first()
    if user is not None:
        if user.check_password(user_data["password"]):
            token = create_access_token(identity=user_data["email"])
            response = {"message": "ログインが完了しました", "token": token, "user_id": user.id}
            return response, 200
    message = "ユーザ名かパスワードが間違っています"
    response = {"message": message}
    return response, 400


@device.route("/api/get_status", methods=["GET"])
@jwt_required()
@cross_origin(origins=["http://127.0.0.1:5500"], methods=["GET"])
def get_status():
    state_list = []
    grade_list = []
    name_list = []
    user_list = User.query.order_by(User.grade.desc())  # 学年順
    for user in user_list:
        latest_time = (
            CheckTime.query.filter_by(user_id=int(user.id))
            .order_by(CheckTime.id.desc())
            .first()
        )
        state_list.append(latest_time.status) if latest_time else state_list.append(6)
        grade_list.append(user.grade)
        name_list.append(user.username)

    # データをJSONに変換して返す
    response = {
        "user_list": [
            {"username": name, "grade": grade, "status": status}
            for name, grade, status in zip(name_list, grade_list, state_list)
        ]
    }

    return response, 200


@device.route("/api/me/check_times", methods=["GET"])
@jwt_required()
@cross_origin(origins=["http://127.0.0.1:5500"], methods=["GET"])
def get_my_times():
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).first()
    page = request.args.get("offset", 1, type=int)
    per_page = request.args.get("limit", 10, type=int)

    times = (
        CheckTime.query.filter_by(user_id=int(user.id))
        .order_by(CheckTime.id.desc())
        .paginate(page=page, per_page=per_page)
    )

    times = times.items

    full_url = request.url

    try:
        next_times = (
            CheckTime.query.filter_by(user_id=int(user.id))
            .order_by(CheckTime.id.desc())
            .paginate(page=page + 1, per_page=per_page)
        )
    except Exception as e:
        next_times = None

    if next_times:
        next_url = full_url.replace("offset=" + str(page), "offset=" + str(page + 1))
    else:
        next_url = None

    response = {
        "check_times": [
            {
                "in_time": time.in_time.isoformat().split(".")[0] + "+09:00"
                if time.in_time
                else None,
                "out_time": time.out_time.isoformat().split(".")[0] + "+09:00"
                if time.out_time
                else None,
                "status": time.status,
                "id": time.id,
            }
            for time in times
        ],
        "next": next_url,
    }
    return response, 200


@device.route("/api/regist_time", methods=["POST"])
@cross_origin(origins=["http://127.0.0.1:5500"], methods=["POST"])
def regist_time():
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
