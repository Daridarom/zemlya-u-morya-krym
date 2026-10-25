#!/usr/bin/env python3
"""Безопасная HTTP-проверка нового домена. Не отправляет заявки."""
from __future__ import annotations
import argparse
import sys
from urllib.request import Request, urlopen
from urllib.error import URLError

def fetch(url: str):
    try:
        req = Request(url,headers={"User-Agent":"TochkaLandingSmokeTest/1.0"})
        with urlopen(req, timeout=15) as rsp:
            return rsp.status, rsp.read(), rsp.headers.get("Content-Type","")
    except (URLError, OSError) as e:
        return 0, str(e).encode(), ""

p=argparse.ArgumentParser()
p.add_argument("base_url",help="https://имя-домена.ru/")
p.add_argument("--production",action="store_true")
a=p.parse_args()
base=a.base_url.rstrip("/") + "/"
if not base.startswith("https://"):
    p.error("Для рабочего сайта нужен HTTPS")
tests=[]
def report(label,ok,details=""):
    tests.append(ok)
    print(("OK" if ok else "FAIL"),label,details)
status,data,ctype=fetch(base)
html=data.decode("utf-8","replace")
report("главная",status==200,f"HTTP {status}")
for marker in ["2 000 000 ₽","1 500 000 ₽","1 200 000 ₽","+7 978 296-41-08","id=\"snt-kerch\"","forms.yandex.ru/u/6adc777e852af3c4d5fc9a8f"]:
    report("содержимое: "+marker,marker in html)
report("основные схемы",all(f'plot-{id}.svg' in html for id in ("1587","1621","2273")))
if a.production:
    report("рабочая версия без noindex",'noindex' not in html.lower())
    report("рабочая версия без плашки",'class="proto-bar"' not in html)
else:
    report("прототип noindex",'noindex' in html.lower())
for path in ("politika.html","assets/style.css","assets/main.js","assets/img/plot-1587.svg","assets/img/plot-1621.svg","assets/img/plot-2273.svg","robots.txt"):
    code,body,typ=fetch(base+path)
    report(path,code==200 and len(body)>0,f"HTTP {code}, {len(body)} B")
print("\nИтог: HTTP- и содержательные проверки выполнены. Отправка формы, CRM и модерация Директа НЕ проверены.")
sys.exit(0 if all(tests) else 2)
