import json
import os

import httpx

from libs.applibs import constants


def abs_path(*path):
    return os.path.join(constants.PROJECT_DIR, *path)


cookies_file = "data/connection/cookies.json"


# Convert cookies to a dictionary
def cookies_to_dict(cookies):
    if isinstance(cookies, httpx.Cookies):
        return {key: cookie for key, cookie in cookies.items()}
    elif isinstance(cookies, dict):
        return cookies
    raise TypeError("Unsupported cookie type")


# Convert dictionary to cookies
def dict_to_cookies(cookie_dict):
    cookies = httpx.Cookies()
    for key, value in cookie_dict.items():
        cookies.set(key, value)
    return cookies


# ronous function to load cookies from a file
def load_cookies():
    if os.path.exists(cookies_file):
        with open(cookies_file, mode="r") as f:
            cookies_dict = json.loads(f.read())
            return dict_to_cookies(cookies_dict)
    return httpx.Cookies()


# ronous function to save cookies to a file
def save_cookies(cookies):
    cookies_dict = cookies_to_dict(cookies)
    with open(cookies_file, mode="w") as f:
        f.write(json.dumps(cookies_dict))
