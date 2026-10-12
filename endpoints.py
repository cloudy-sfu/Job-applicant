import json
import os
import re
from pathlib import Path

from flask import Flask, request
from linkdapi import LinkdAPI
from selenium.common.exceptions import NoSuchWindowException

from database import connect, set_config, unset_config, get_config
from universities import SearchUniversity

app = Flask(__name__)
os.makedirs("raw", exist_ok=True)
insert_profile_fp = Path("sqls/insert_profile.sql").resolve()

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
            try:
                current_url = driver.current_url
            except NoSuchWindowException:
                if len(driver.window_handles) == 1:
                    driver.switch_to.window(driver.window_handles[0])
                    current_url = driver.current_url
                else:
                    return {
                        "error_code": 1,
                        "error": "Cannot parse current profile. Potential reason: you "
                                 "used \"Restore pages\" in the current window. Please "
                                 "close the browser, wait 2 seconds, and start the "
                                 "program again."
                    }
        profile_id_match = re.search(r"in/(.+?)(?:[/?]|$)", current_url)
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

    # Get profile
    linkdapi_key = get_config("LINKDAPI_KEY")
    client = LinkdAPI(api_key=linkdapi_key)
    profile = client.get_full_profile(username=profile_id)['data']

    # Add school's country
    search_engine = SearchUniversity()
    for education in profile['educations']:
        school_info = search_engine.search_university(education['schoolName'])
        education['country'] = school_info.get("country", "")

    # Aggregate roles of the same company
    companies = {}
    for position in profile['fullPositions']:
        employer = {}
        role = {}
        for k, v in position.items():
            if k.startswith("company"):
                employer[k] = v
            else:
                role[k] = v
        company_id = position["companyId"]
        employer['country'] = position['location'].split(',')[-1].strip()
        if company_id in companies.keys():
            companies[company_id]['roles'].append(role)
        else:
            companies[company_id] = employer
            companies[company_id]['roles'] = [role]
    profile['fullPositions'] = companies

    # Add contact information
    contact_info = client.get_contact_info(profile_id)['data']
    profile.update(contact_info)

    profile_json = json.dumps(profile)
    c = connect()
    with c:
        c.execute(
            insert_profile_fp.read_text(),
            {"profile_id": profile_id, "profile": profile_json}
        )

    return {
        "error_code": 0
    }
