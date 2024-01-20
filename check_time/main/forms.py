from check_time.models import User, CheckTime
from flask_wtf import FlaskForm
from wtforms import (
    PasswordField,
    StringField,
    SubmitField,
    ValidationError,
    IntegerField,
    DateTimeField
)
from wtforms.validators import DataRequired, Email, EqualTo
from sqlalchemy import or_, and_



class UpdataTimeForm(FlaskForm):
    
    in_time = DateTimeField("入室時間", validators=[DataRequired()], format='%Y-%m-%dT%H:%M')
    out_time = DateTimeField("退室時間", validators=[DataRequired()], format='%Y-%m-%dT%H:%M')
    status = StringField("状態", validators=[DataRequired()])
    submit = SubmitField("更新")

    def __init__(self, check_time_id, user_id, *args, **kwargs):
       super(UpdataTimeForm, self).__init__(*args, **kwargs)
       self.id = check_time_id
       self.user_id = user_id

    def validate_in_time(self, field):
        # 入室時間が他のレコードの入退室室時間と被っていないか確認
        overlapping_record = CheckTime.query.filter(
            CheckTime.id != self.id,
            CheckTime.user_id == self.user_id,
            and_(
                CheckTime.in_time <= field.data,
                CheckTime.out_time >= field.data
            )
            ).first()
        
        if overlapping_record:
            raise ValidationError("入力された入室時間は他の入退室記録と被っているため無効です")


        

    def validate_out_time(self, field):
        # 退室時間が他のレコードの入退室時間と被っていないか確認
        overlapping_record1 = CheckTime.query.filter(
            CheckTime.id != self.id,
            CheckTime.user_id == self.user_id,
                and_(
                    CheckTime.in_time <= field.data,
                    CheckTime.out_time >= field.data
                )
        ).first()
        overlapping_record2 = CheckTime.query.filter(
            CheckTime.id != self.id,
            CheckTime.user_id == self.user_id,
                and_(
                    CheckTime.in_time >= self.in_time.data,
                    CheckTime.out_time <= field.data
                )
        ).first()
        if overlapping_record1:
            raise ValidationError("入力された退室時間は他の入退室記録と被っているため無効です")
        if overlapping_record2:
            raise ValidationError("入力された入室時間と退室時間の中に他の入退室記録があるため無効です")
        # in_time よりも前の時間を out_time に入力できないように検証
        if self.in_time.data and field.data and self.in_time.data > field.data:
            raise ValidationError("退室時間は入室時間よりも後の時間にしてください")


    def validate_status(self, field):
        if not (0 <= int(field.data) <= 6):
            raise ValidationError("存在しない状態です")
        

