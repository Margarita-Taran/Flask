import os

import flask
import pydantic
from flask import jsonify, request
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError

import schema
from models import Session, Ad

app = flask.Flask("app")


class HttpError(Exception):
    def __init__(self, status_code: int, error_message: dict | str | list):
        self.status_code = status_code
        self.error_message = error_message


@app.errorhandler(HttpError)
def error_handler(er: HttpError):
    response = jsonify({"error": er.error_message})
    response.status_code = er.status_code
    return response


@app.before_request
def before_request():
    session = Session()
    request.session = session


@app.after_request
def after_request(http_response: flask.Response):
    request.session.close()
    return http_response


def validate(json_data: dict, schema_cls: type[schema.CreateAd] | type[schema.UpdateAd]):
    try:
        return schema_cls(**json_data).dict(exclude_unset=True)
    except pydantic.ValidationError as err:
        errors = err.errors()
        for error in errors:
            error.pop("ctx", None)
        raise HttpError(400, errors)


def get_ad_by_id(ad_id):
    ad = request.session.get(Ad, ad_id)
    if ad is None:
        raise HttpError(404, "ad not found")
    return ad


def add_ad(ad):
    request.session.add(ad)
    try:
        request.session.commit()
    except IntegrityError:
        raise HttpError(409, "ad already exists")
    return ad


class AdView(MethodView):
    def get(self, ad_id):
        ad = get_ad_by_id(ad_id)
        return jsonify(ad.dict)

    def post(self):
        json_data = validate(request.json, schema.CreateAd)
        ad = Ad(**json_data)
        ad = add_ad(ad)
        return jsonify(ad.dict)

    def patch(self, ad_id: int):
        json_data = validate(request.json, schema.UpdateAd)
        ad = get_ad_by_id(ad_id)
        for field, value in json_data.items():
            setattr(ad, field, value)
        request.session.commit()
        return jsonify(ad.dict)

    def delete(self, ad_id: int):
        ad = get_ad_by_id(ad_id)
        request.session.delete(ad)
        request.session.commit()
        return jsonify({"status": "deleted"})


ad_view = AdView.as_view("ad")

app.add_url_rule("/ad/", view_func=ad_view, methods=["POST"])
app.add_url_rule("/ad/<int:ad_id>/", view_func=ad_view, methods=["GET", "PATCH", "DELETE"])

if __name__ == "__main__":
    app.run()
