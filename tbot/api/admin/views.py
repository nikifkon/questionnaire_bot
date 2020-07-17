import flask_admin as admin
import flask_login as login
from flask import redirect, request, url_for
from flask_admin import expose, helpers
from flask_admin.contrib import sqla
from pydantic import ValidationError as PydanticValidationError
from wtforms import TextAreaField
from wtforms.validators import ValidationError

from tbot import schemas
from tbot.utils import session_scope
from .forms import LoginForm


# Create customized model view class
class MyModelView(sqla.ModelView):

    def is_accessible(self):
        return login.current_user.is_authenticated


# Create customized index view class that handles login & registration
class MyAdminIndexView(admin.AdminIndexView):

    @expose("/")
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for(".login_view"))
        return super(MyAdminIndexView, self).index()

    @expose("/login/", methods=("GET", "POST"))
    def login_view(self):
        # handle user login
        with session_scope() as session:
            form = LoginForm(request.form)
            if helpers.validate_form_on_submit(form):
                user = form.get_user(session)
                login.login_user(user)

            if login.current_user.is_authenticated:
                return redirect(url_for(".index"))
            self._template_args["form"] = form
            return super(MyAdminIndexView, self).index()

    @expose("/logout/")
    def logout_view(self):
        login.logout_user()
        return redirect(url_for(".index"))


class UserView(MyModelView):
    pass


class HouseView(MyModelView):
    form_excluded_columns = ("events", "users",)


class AccountView(MyModelView):
    pass


class AreaView(MyModelView):
    form_excluded_columns = ("houses", "events")


EMERGENCY = schemas.EventType.EMERGENCY
SCHEDUELD_WORK = schemas.EventType.SCHEDUELD_WORK
UNSCHEDUELD_WORK = schemas.EventType.UNSCHEDUELD_WORK

ALL = schemas.EventTarget.ALL
HOUSE = schemas.EventTarget.HOUSE
AREA = schemas.EventTarget.AREA


class EventView(MyModelView):
    form_overrides = {
        "description": TextAreaField
    }
    form_excluded_columns = ("messages",)
    column_exclude_list = ("description",)

    form_choices = {
        "type": [
            (EMERGENCY.value, EMERGENCY.value),
            (SCHEDUELD_WORK.value, SCHEDUELD_WORK.value),
            (UNSCHEDUELD_WORK.value, UNSCHEDUELD_WORK.value),
        ],
        "target": [
            (ALL.value, ALL.value),
            (HOUSE.value, HOUSE.value),
            (AREA.value, AREA.value),
        ]
    }

    def on_model_change(self, form, model, is_created):
        data = form.data
        data["area"] = schemas.Area.from_orm(data["area"])
        data["house"] = schemas.House.from_orm(data["house"])
        try:
            if is_created:
                schemas.EventCreate(**data)
            else:
                data["id"] = model.id
                schemas.EventUpdate(**data)
        except PydanticValidationError as exc:
            error = exc.errors()[0]
            msg = "Error in '{loc[0]}': {msg}".format(**error)
            raise ValidationError(msg)
        return model
