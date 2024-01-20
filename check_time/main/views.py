from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import login_required
from check_time import db
from check_time.models import User, CheckTime
from check_time.users.forms import LoginForm, RegistrationForm, UpdataUserForm
from check_time.main.forms import UpdataTimeForm
from flask_login import current_user, login_required, login_user, logout_user
from pytz import timezone
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

main = Blueprint("main", __name__)


@main.route("/state_list")
@login_required
def state_list():
    state_list = []
    user_list = User.query.order_by(User.grade.desc())  # 学年順
    for user in user_list:
        latest_time = (
            CheckTime.query.filter_by(user_id=int(user.id))
            .order_by(CheckTime.id.desc())
            .first()
        )
        state_list.append(latest_time.status) if latest_time else state_list.append(6)
    return render_template(
        "main/state_list.html", user_list=user_list, state_list=state_list
    )

@main.route('/<int:user_id>//check_time_maintenance' , methods=['GET', 'POST'])
@login_required
def check_time_maintenance(user_id):
    page = request.args.get('page', 1, type=int)
    check_times = CheckTime.query.filter_by(user_id = user_id).order_by(CheckTime.id.desc()).paginate(page=page, per_page=10)
    return render_template('check_time_maintenance.html', check_times=check_times)

@main.route("/<int:check_time_id>/check_time_edit", methods=["GET", "POST"])
@login_required
def check_time_edit(check_time_id):
    check_time = CheckTime.query.get_or_404(check_time_id)
    form = UpdataTimeForm(check_time_id, current_user.id)
    if form.validate_on_submit():
        check_time.in_time = form.in_time.data
        check_time.out_time = form.out_time.data
        check_time.status = form.status.data
        db.session.commit()
        flash("入退室に関する情報が更新されました")

        return redirect(url_for('main.check_time_maintenance', user_id = current_user.id))
    elif request.method == "GET":
        form.in_time.data = check_time.in_time
        form.out_time.data = check_time.out_time
        form.status.data = check_time.status
    return render_template("check_time_edit.html", form=form)



@main.route('/<int:check_time_id>/delete_check_time', methods=['GET', 'POST'])
@login_required
def delete_check_time(check_time_id):
    # Assuming you have a CheckTime model
    check_times_to_delete = CheckTime.query.filter_by(id=check_time_id).all()

    if not check_times_to_delete:
        abort(404)

    # Delete the entries
    for check_time in check_times_to_delete:
        db.session.delete(check_time)

    # Commit the changes
    db.session.commit()

    flash('入退室情報が削除されました')
    return redirect(url_for('main.check_time_maintenance', user_id = current_user.id))



@main.route("/")
def home():
    return render_template("main/home.html")
