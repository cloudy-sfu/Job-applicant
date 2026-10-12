import os

from flask import Flask, request

from database import set_config, unset_config, get_config

app = Flask(__name__)
os.makedirs("raw", exist_ok=True)


@app.route('/set_linkdapi_key', methods=['POST'])
def set_linkdapi_key():
    linkdapi_key = request.form.get('linkdapi_key')
    if linkdapi_key:
        set_config("LINKDAPI_KEY", linkdapi_key)
    else:
        unset_config("LINKDAPI_KEY")
    return ''


@app.route('/get_linkdapi_key')
def get_linkdapi_key():
    return get_config("LINKDAPI_KEY")
