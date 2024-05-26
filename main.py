import json
import requests
import urllib.parse
import time
import datetime
import random
import os
from cache import cache


max_api_wait_time = 3
max_time = 10
apis = [r"https://youtube.076.ne.jp/",r"https://vid.puffyan.us/",r"https://inv.riverside.rocks/",r"https://invidio.xamh.de/",r"https://y.com.sb/",r"https://invidious.sethforprivacy.com/",r"https://invidious.tiekoetter.com/",r"https://inv.bp.projectsegfau.lt/",r"https://inv.vern.cc/",r"https://invidious.nerdvpn.de/",r"https://inv.privacy.com.de/",r"https://invidious.rhyshl.live/",r"https://invidious.slipfox.xyz/",r"https://invidious.weblibre.org/",r"https://invidious.namazso.eu/"]
url = requests.get(r'https://raw.githubusercontent.com/mochidukiyukimi/yuki-youtube-instance/main/instance.txt').text.rstrip()
version = "1.0"

apichannels = []
apicomments = []
[[apichannels.append(i),apicomments.append(i)] for i in apis]
class APItimeoutError(Exception):
    pass

def is_json(json_str):
    result = False
    try:
        json.loads(json_str)
        result = True
    except json.JSONDecodeError as jde:
        pass
    return result

def apirequest(url):
    global apis
    global max_time
    starttime = time.time()
    for api in apis:
        if  time.time() - starttime >= max_time -1:
            break
        try:
            res = requests.get(api+url,timeout=max_api_wait_time)
            if res.status_code == 200 and is_json(res.text):
                return res.text
            else:
                print(f"エラー:{api}")
                apis.append(api)
                apis.remove(api)
        except:
            print(f"タイムアウト:{api}")
            apis.append(api)
            apis.remove(api)
    raise APItimeoutError("APIがタイムアウトしました")

def apichannelrequest(url):
    global apichannels
    global max_time
    starttime = time.time()
    for api in apichannels:
        if  time.time() - starttime >= max_time -1:
            break
        try:
            res = requests.get(api+url,timeout=max_api_wait_time)
            if res.status_code == 200 and is_json(res.text):
                return res.text
            else:
                print(f"エラー:{api}")
                apichannels.append(api)
                apichannels.remove(api)
        except:
            print(f"タイムアウト:{api}")
            apichannels.append(api)
            apichannels.remove(api)
    raise APItimeoutError("APIがタイムアウトしました")

def apicommentsrequest(url):
    global apicomments
    global max_time
    starttime = time.time()
    for api in apicomments:
        if  time.time() - starttime >= max_time -1:
            break
        try:
            res = requests.get(api+url,timeout=max_api_wait_time)
            if res.status_code == 200 and is_json(res.text):
                return res.text
            else:
                print(f"エラー:{api}")
                apicomments.append(api)
                apicomments.remove(api)
        except:
            print(f"タイムアウト:{api}")
            apicomments.append(api)
            apicomments.remove(api)
    raise APItimeoutError("APIがタイムアウトしました")


def get_info(request):
    global version
    return json.dumps([version,os.environ.get('RENDER_EXTERNAL_URL'),str(request.scope["headers"]),str(request.scope['router'])[39:-2]])
    


def check_cokie(cookie):
    if cookie == "True":
        return True
    return False





from fastapi import FastAPI, Depends
from fastapi import Response,Cookie,Request
from fastapi.responses import HTMLResponse,PlainTextResponse
from fastapi.responses import RedirectResponse as redirect
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Union


app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/css", StaticFiles(directory="./css"), name="static")
app.mount("/blog", StaticFiles(directory="./blog", html=True), name="static")
app.add_middleware(GZipMiddleware, minimum_size=1000)

from fastapi.templating import Jinja2Templates
template = Jinja2Templates(directory='templates').TemplateResponse





@app.get("/", response_class=HTMLResponse)
def home(response: Response,request: Request,yuki: Union[str] = Cookie(None)):
    if check_cokie(yuki):
        response.set_cookie("yuki","True",max_age=60 * 60 * 24 * 7)
        return template("home.html",{"request": request})
    return redirect("/blog")

@app.get("/answer", response_class=HTMLResponse)
def set_cokie(q:str):
    if q.count() > 10:
        return "ランダム"
    return "文章"


@app.get("/info", response_class=HTMLResponse)
def viewlist(response: Response,request: Request,yuki: Union[str] = Cookie(None)):
    global apis,apichannels,apicomments
    if not(check_cokie(yuki)):
        return redirect("/")
    response.set_cookie("yuki","True",max_age=60 * 60 * 24 * 7)
    return template("info.html",{"request": request,"Youtube_API":apis[0],"Channel_API":apichannels[0],"Comments_API":apicomments[0]})

@app.get("/bbs",response_class=HTMLResponse)
def view_bbs(request: Request,name: Union[str, None] = "",seed:Union[str,None]="",channel:Union[str,None]="main",verify:Union[str,None]="false",yuki: Union[str] = Cookie(None)):
    if not(check_cokie(yuki)):
        return redirect("/")
    res = HTMLResponse(requests.get(fr"{url}bbs?name={urllib.parse.quote(name)}&seed={urllib.parse.quote(seed)}&channel={urllib.parse.quote(channel)}&verify={urllib.parse.quote(verify)}",cookies={"yuki":"True"}).text)
    return res

@cache(seconds=5)
def bbsapi_cached(verify,channel):
    return requests.get(fr"{url}bbs/api?t={urllib.parse.quote(str(int(time.time()*1000)))}&verify={urllib.parse.quote(verify)}&channel={urllib.parse.quote(channel)}",cookies={"yuki":"True"}).text

@app.get("/bbs/api",response_class=HTMLResponse)
def view_bbs(request: Request,t: str,channel:Union[str,None]="main",verify: Union[str,None] = "false"):
    print(fr"{url}bbs/api?t={urllib.parse.quote(t)}&verify={urllib.parse.quote(verify)}&channel={urllib.parse.quote(channel)}")
    return bbsapi_cached(verify,channel)

@app.get("/bbs/result")
def write_bbs(request: Request,name: str = "",message: str = "",seed:Union[str,None] = "",channel:Union[str,None]="main",verify:Union[str,None]="false",yuki: Union[str] = Cookie(None)):
    if not(check_cokie(yuki)):
        return redirect("/")
    t = requests.get(fr"{url}bbs/result?name={urllib.parse.quote(name)}&message={urllib.parse.quote(message)}&seed={urllib.parse.quote(seed)}&channel={urllib.parse.quote(channel)}&verify={urllib.parse.quote(verify)}&info={urllib.parse.quote(get_info(request))}",cookies={"yuki":"True"}, allow_redirects=False)
    if t.status_code != 307:
        return HTMLResponse(t.text)
    return redirect(f"/bbs?name={urllib.parse.quote(name)}&seed={urllib.parse.quote(seed)}&channel={urllib.parse.quote(channel)}&verify={urllib.parse.quote(verify)}")

@cache(seconds=30)
def how_cached():
    return requests.get(fr"{url}bbs/how").text

@app.get("/bbs/how",response_class=PlainTextResponse)
def view_commonds(request: Request,yuki: Union[str] = Cookie(None)):
    if not(check_cokie(yuki)):
        return redirect("/")
    return how_cached()

@app.get("/load_instance")
def home():
    global url
    url = requests.get(r'https://raw.githubusercontent.com/mochidukiyukimi/yuki-youtube-instance/main/instance.txt').text.rstrip()


@app.exception_handler(500)
def page(request: Request,__):
    return template("APIwait.html",{"request": request},status_code=500)

@app.exception_handler(APItimeoutError)
def APIwait(request: Request,exception: APItimeoutError):
    return template("APIwait.html",{"request": request},status_code=500)
