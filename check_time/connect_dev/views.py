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
from datetime import datetime, timedelta
from pytz import timezone
import time
from wtforms import ValidationError
from flask_jwt_extended import (
    jwt_required,
    create_access_token,
    JWTManager,
    get_jwt_identity,
)
from sqlalchemy import func


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
        token = create_access_token(
            identity=user_data["email"], expires_delta=timedelta(days=30)
        )
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
            token = create_access_token(
                identity=user_data["email"], expires_delta=timedelta(days=30)
            )
            response = {"message": "ログインが完了しました", "token": token, "user_id": user.id}
            return response, 200
    message = "ユーザ名かパスワードが間違っています"
    response = {"message": message}
    return response, 400


@device.route("/api/change_nfc", methods=["POST"])
@cross_origin(origins=["http://127.0.0.1:5500"], methods=["POST"])
def change_nfc():
    user_data = request.get_json()
    print(user_data)
    user = User.query.filter_by(email=user_data["email"]).first()
    if user is not None:
        if user.check_password(user_data["password"]):
            user.nfc_id = user_data["nfc_id"]
            db.session.commit()
            response = {"message": "NFCタグの更新が完了しました"}
            return response, 200
        else:
            message = "ユーザ名かパスワードが間違っています"
            response = {"message": message}
            return response, 400
    else:
        message = "ユーザ名かパスワードが間違っています"
        response = {"message": message}
        return response, 400


@device.route("/api/get_status", methods=["GET"])
@jwt_required()
@cross_origin(origins=["http://127.0.0.1:5500"], methods=["GET"])
def get_status():
    today = datetime.now().date()
    state_list = []
    grade_list = []
    name_list = []
    time_today_list = []
    time_week_list = []
    time_month_list = []
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

        # 今日の時間の合計を取得
        time_today = (
            db.session.query(func.sum(CheckTime.out_time - CheckTime.in_time))
            .filter(
                CheckTime.user_id == user.id,
                CheckTime.in_time >= today,
                CheckTime.in_time < today + timedelta(days=1),
            )
            .scalar()
        )

        # 今週の時間の合計を取得（月曜日から日曜日までを1週間とする）
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=7)
        time_week = (
            db.session.query(func.sum(CheckTime.out_time - CheckTime.in_time))
            .filter(
                CheckTime.user_id == user.id,
                CheckTime.in_time >= start_of_week,
                CheckTime.in_time < end_of_week,
            )
            .scalar()
        )

        # 今月の時間の合計を取得
        start_of_month = datetime(today.year, today.month, 1)
        end_of_month = (
            datetime(today.year, today.month + 1, 1)
            if today.month < 12
            else datetime(today.year + 1, 1, 1)
        )
        time_month = (
            db.session.query(func.sum(CheckTime.out_time - CheckTime.in_time))
            .filter(
                CheckTime.user_id == user.id,
                CheckTime.in_time >= start_of_month,
                CheckTime.in_time < end_of_month,
            )
            .scalar()
        )

        time_today_list.append(
            int(time_today.total_seconds() // 60)
        ) if time_today else time_today_list.append(0)
        time_week_list.append(
            int(time_week.total_seconds() // 60)
        ) if time_week else time_week_list.append(0)
        time_month_list.append(
            int(time_month.total_seconds() // 60)
        ) if time_month else time_month_list.append(0)
    # データをJSONに変換して返す
    response = {
        "user_list": [
            {
                "username": name,
                "grade": grade,
                "status": status,
                "time_today": time_today,
                "time_week": time_week,
                "time_month": time_month,
            }
            for name, grade, status, time_today, time_week, time_month in zip(
                name_list,
                grade_list,
                state_list,
                time_today_list,
                time_week_list,
                time_month_list,
            )
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

    try:
        next_times = (
            CheckTime.query.filter_by(user_id=int(user.id))
            .order_by(CheckTime.id.desc())
            .paginate(page=page + 1, per_page=per_page)
        )
    except Exception as e:
        next_times = None

    if next_times:
        next_page = page + 1
    else:
        next_page = None

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
        "next": next_page,
    }
    return response, 200


@device.route("/api/regist_time", methods=["POST"])
@cross_origin(origins=["http://127.0.0.1:5500"], methods=["POST"])
def regist_time():
    time_data = request.get_json()
    print(time_data["nfc_id"])
    user = User.query.filter_by(nfc_id=time_data["nfc_id"]).first()
    print(user)
    if user is None:
        response = {"message": "登録されていないNFCタグです"}
        return response, 400
    check_time = (
        CheckTime.query.filter_by(user_id=user.id).order_by(CheckTime.id.desc()).first()
    )
    if check_time is None:
        if time_data["status"] == 0:
            in_time = CheckTime(
                user_id=user.id,
                in_time=datetime.now(timezone("Asia/Tokyo")).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            )
            db.session.add(in_time)
            db.session.commit()
            response = {"message": "頑張ってください"}
            return response, 200
        else:
            response = {"message": "前回の退室時間が記録されていません"}
            return response, 400
    else:
        if time_data["status"] > 0:
            if check_time.out_time is None:
                check_time.out_time = datetime.now(timezone("Asia/Tokyo")).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
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
                    in_time=datetime.now(timezone("Asia/Tokyo")).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                )
                db.session.add(in_time)
                db.session.commit()
                response = {"message": "頑張ってください"}
                return response, 200
