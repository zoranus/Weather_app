import datetime as dt
import json

import requests
from flask import Flask, jsonify, request


API_TOKEN = ""
RSA_KEY =""

app = Flask(__name__)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def home_page():
    return "<p><h2>TEST</h2></p>"


def get_weather(weather_info):
    url_base = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"
    loc = weather_info["location"]
    date = weather_info["date"]
    url = f"{url_base}/{loc}/{date}/?key={RSA_KEY}&contentType=json"

    response = requests.get(url)

    if response.status_code == requests.codes.ok:
        return json.loads(response.text)
    else:
        raise InvalidUsage(response.text, status_code=response.status_code)


@app.route("/content/api/v1/integration/generate", methods=["POST"])
def weather_endpoint():
    date_utc = dt.datetime.now()
    json_data = request.get_json()

    if json_data.get("token") is None:
        raise InvalidUsage("token is required", status_code=400)

    token = json_data.get("token")

    if token != API_TOKEN:
        raise InvalidUsage("wrong API token", status_code=403)

    weather = get_weather(json_data)
    w_list = []
    for metric in ["temp", "windspeed", "pressure", "humidity"]:
        w_list.append(weather["days"][0][metric])
        
    result = {  
    "requester_name": json_data.get("requester_name"), 
    "timestamp": date_utc,
    "location": json_data.get("location"),
    "date": json_data.get("date"),
    "weather":
    {
    "temp_c": w_list[0],
    "wind_kph": w_list[1],
    "pressure_mb": w_list[2],
    "humidity": w_list[3]
    }
    }

    return result
