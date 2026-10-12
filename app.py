import json
import os
import socket
import time
from pathlib import Path
from threading import Lock, Thread

import selenium.common as common
import selenium.webdriver as webdriver

from database import g, connect
from endpoints import app


def find_available_port(start_port: int, end_port: int):
    for port_ in range(start_port, end_port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(("127.0.0.1", port_))
            s.close()
            return port_
        except OSError:
            pass
    raise Exception(f"No available port in interval [{start_port}, {end_port}).")


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


os.makedirs("raw/selenium_user_data", exist_ok=True)

# Get port
port = find_available_port(1024, 65536)

# Write port to manifest.json of Chrome extension
ext_fp = Path("chrome_extension").resolve()
with open(ext_fp / "manifest.template.json", "r") as f:
    manifest = json.load(f)
manifest["host_permissions"].append(f"http://127.0.0.1:{port}/*")
with open(ext_fp / "manifest.json", "w") as f:
    json.dump(manifest, f, indent=2)
(ext_fp / "flask_port.js").write_text(
    f"export const flask_port = {port};"
)

# Initialize database
create_schema_fp = Path("sqls/create_schema.sql").resolve()
with app.app_context():
    c = connect()
    with c:
        for statement in create_schema_fp.read_text().split(';'):
            c.execute(statement)

# Launch Flask application
# daemon=True -> Python process will exit when the browser is closed
flask_thread = Thread(target=app.run, kwargs={"port": port}, daemon=True)
flask_thread.start()

# Define browser options
options = webdriver.chrome.options.Options()
options.enable_bidi = True
options.add_argument("--remote-debugging-pipe")
options.add_argument("--enable-unsafe-extension-debugging")
# Hide "Chrome is being controlled by automated test software" banner
options.add_experimental_option("excludeSwitches", ["enable-automation"])
# Create browser profile
selenium_fp = Path("raw/selenium_user_data").resolve()
options.add_argument(f"--user-data-dir={selenium_fp}")
# Ban "Restore pages"
options.add_experimental_option("prefs", {
    "profile.exit_type": "Normal",
    "profile.exited_cleanly": True,
})

# Create browser instance
driver = webdriver.Chrome(options=options)
# Install "Job applicant" extension
thread_lock = Lock()
with thread_lock:
    driver.webextension.install(path=str(ext_fp))
    driver.get("chrome://new-tab-page/")
    app.extensions["selenium_browser"] = {
        "driver": driver,
        "lock": thread_lock,
    }

# Exit when the user closes the browser
while 1:
    try:
        with thread_lock:
            assert driver.window_handles
    except (AssertionError, common.exceptions.WebDriverException,
            common.exceptions.NoSuchWindowException, ):
        break
    else:
        time.sleep(1)
with thread_lock:
    driver.quit()
