import os

import dotenv
from flask import Flask, render_template, request, redirect

app = Flask(__name__)
dotenv.load_dotenv()


@app.route('/set_linkdapi_key', methods=['POST'])
def set_linkdapi_key():
    config = dotenv.find_dotenv()
    linkdapi_key = request.form.get('linkdapi_key')
    if linkdapi_key:
        dotenv.set_key(config, "LINKDAPI_KEY", linkdapi_key)
        os.environ["LINKDAPI_KEY"] = linkdapi_key
    else:
        dotenv.unset_key(config, "LINKDAPI_KEY")
        if "LINKDAPI_KEY" in os.environ.keys():
            del os.environ["LINKDAPI_KEY"]
    return ''


@app.route('/get_linkdapi_key')
def get_linkdapi_key():
    linkdapi_key = os.environ.get("LINKDAPI_KEY", default="")
    return linkdapi_key
