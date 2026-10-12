import os
import re

from flask import Flask, request

from database import get_db, set_config, unset_config, get_config
from linkdapi import LinkdAPI
from universities import SearchUniversity

app = Flask(__name__)
os.makedirs("raw", exist_ok=True)

@app.route('/set_linkdapi_key', methods=['POST'])
def set_linkdapi_key():
    linkdapi_key = request.form.get('linkdapi_key')
    if linkdapi_key:
        set_config("LINKDAPI_KEY", linkdapi_key)
    else:
        unset_config("LINKDAPI_KEY")
    return {"error_code": 0}


@app.route('/init_vars')
def init_vars():
    return {
        "linkdapi_key": get_config("LINKDAPI_KEY"),
    }


@app.route('/add_linkedin_profile', methods=['POST'])
def add_linkedin_profile():
    # Get profile ID
    if request.form.get('use_current_linkedin_profile') == 'on':
        with app.extensions["selenium_browser"]["lock"]:
            driver = app.extensions["selenium_browser"]["driver"]
            current_url = driver.current_url
        profile_id_match = re.search(r"in/(.+?)/?", current_url)
        if not profile_id_match:
            return {
                "error_code": 1,
                "error": f"Current URL is {current_url}, not a valid LinkedIn profile."
            }
        profile_id = profile_id_match.group(1)
    else:
        profile_id = request.form.get('linkedin_profile')
    if not profile_id:
        return {
            "error_code": 1,
            "error": f"LinkedIn profile ID cannot be empty."
        }

    return {
        "error_code": 0
    }
