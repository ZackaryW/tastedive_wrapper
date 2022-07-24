import typing
import requests
from bs4 import BeautifulSoup

API_KEY = None

API_LIMIT = None

tk_cs : str = "compact"
tk_vl : int = None
tk_r: str = None
tk_s: str = None

_csrf_token : str = None

def setAPIKey(api_key : str):
    if api_key is None:
        return

    if not isinstance(api_key, str):
        raise TypeError("api_key must be a string")

    global API_KEY
    API_KEY = api_key

def getCSRF():
    return _csrf_token

def _loadCookies(cookies : dict):
    global tk_r, tk_s, _csrf_token
    if len(cookies) == 0:
        if "tk_r" not in cookies and tk_r is not None:
            cookies["tk_r"] = tk_r
        if "tk_s" not in cookies and tk_s is not None:
            cookies["tk_s"] = tk_s
        if "_csrf_token" not in cookies and _csrf_token is not None:
            cookies["_csrf_token"] = _csrf_token
        if "tk_cs" not in cookies and tk_cs is not None:
            cookies["tk_cs"] = tk_cs
        if "tk_vl" not in cookies and tk_vl is not None:
            cookies["tk_vl"] = str(tk_vl)

    return cookies

def makeRequest(
        url : str, 
        request_method : typing.Callable = requests.get,
        params : dict = {}, 
        headers : dict = {}, 
        data : dict = {},
        cookies : dict = {}
    ) -> requests.Response:

    # verify
    if not isinstance(request_method, typing.Callable):
        raise TypeError("request_method must be a callable")
    if not isinstance(url, str):
        raise TypeError("url must be a string")
    
    # api key
    if API_KEY is not None and url.startswith("https://tastedive.com/api/"):
        params["k"] = API_KEY

    _loadCookies(cookies)

    kwargs = {
        "url": url,
        "headers": headers,
        "params": params,
        "cookies" : cookies,
    }

    if not isinstance(data, dict):
        kwargs["data"] = data
    else:
        kwargs["json"] = data

    _KEEP_VALUE = lambda v : v is not None or (isinstance(v, dict) and len(v) > 0)

    kwargs = {k: v for k, v in kwargs.items() if _KEEP_VALUE(v)}

    return request_method(**kwargs)

def _obtain_csrf_token():
    setting_url = "https://tastedive.com/account/settings"

    req = makeRequest(url=setting_url, cookies={"tk_r": tk_r, "tk_s": tk_s})
    soup = BeautifulSoup(req.text, 'html.parser')
    token = soup.find('input', {'name': '_csrf_token'})

    return token['value']

@typing.overload
def setCookies(cookie_str : str):
    pass    

@typing.overload
def setCookies(cookie_dict : dict):
    pass

def setCookies(cookie_val):
    if cookie_val is None:
        return

    if not isinstance(cookie_val, dict) and not isinstance(cookie_val, str):
        raise TypeError("cookie_val must be a dict or a string")

    global tk_r, tk_s, _csrf_token, tk_cs, tk_vl
 
    if isinstance(cookie_val, str):
        splitted = cookie_val.split(";")
        if not len(splitted) >= 2:
            raise ValueError("cookie_val must be a string with 3 parts")
        for cookie in splitted:
            cookie = cookie.strip()
            if cookie.startswith("tk_r="):
                tk_r = cookie.split("=")[1]
            elif cookie.startswith("tk_s="):
                tk_s = cookie.split("=")[1]
            elif cookie.startswith("_csrf_token="):
                _csrf_token = cookie.split("=")[1]
            elif cookie.startswith("tk_cs="):
                tk_cs = cookie.split("=")[1]
            elif cookie.startswith("tk_vl="):
                tk_vl = cookie.split("=")[1]
    else:

        for k, v in cookie_val.items():
            if k == "tk_r":
                tk_r = v
            elif k == "tk_s":
                tk_s = v
            elif k == "_csrf_token":
                _csrf_token = v
            elif k == "tk_cs":
                tk_cs = v
            elif k == "tk_vl":
                tk_vl = v
            else:
                raise ValueError("unknown cookie key")

    # resolve _csrf_token
    if _csrf_token is None:
        _csrf_token = _obtain_csrf_token()

    pass