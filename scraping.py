from selenium import webdriver
from bs4 import BeautifulSoup
import time
from selenium.common.exceptions import NoSuchElementException
from pymongo import MongoClient
import requests


client = MongoClient('13.209.85.240', 27017, username="test", password="test")
db = client.db_hh_w1_g31

driver = webdriver.Chrome('./chromedriver')

url = "http://matstar.sbs.co.kr/location.html"

driver.get(url)
time.sleep(5)

for i in range(50):
    #위에 50부분을 늘리면 늘릴 수록 더 많은 정보가 들어온다!
    try:
        btn_more = driver.find_element_by_css_selector("#foodstar-front-location-curation-more-self > div > button")
        # ㄴ 셀레니움으로 더보기 버튼을 찾아라!!
        btn_more.click()
        time.sleep(5)
    except NoSuchElementException:
        # ㄴ 가령 더보기 버튼이 없는 마지막 페이지일때 같은 오류상황!
        break

req = driver.page_source
driver.quit()

soup = BeautifulSoup(req, 'html.parser')

places = soup.select("ul.restaurant_list > div > div > li > div > a")
# ㄴ 카드의 선택자
print(len(places))
for place in places:
    title = place.select_one("strong.box_module_title").text
    address = place.select_one("div.box_module_cont > div > div > div.mil_inner_spot > span.il_text").text
    category = place.select_one("div.box_module_cont > div > div > div.mil_inner_kind > span.il_text").text
    show, episode = place.select_one("div.box_module_cont > div > div > div.mil_inner_tv > span.il_text").text.rsplit(" ", 1)
    print(title, address, category, show, episode)
    # ㄴ places 를 돌면서 해당 변수들을 채워주는 값을 가져오는 것!

    headers = {
        "X-NCP-APIGW-API-KEY-ID": "v8sf95acns",
        "X-NCP-APIGW-API-KEY": "2z5pNBeex65cOIC2sjQkcKrKbPZGxTjVyKqcg68G"
    }
    r = requests.get(f"https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode?query={address}", headers=headers)
    response = r.json()
    if response["status"] == "OK":
        if len(response["addresses"]) > 0:
            x = float(response["addresses"][0]["x"])
            # ㄴ 파이썬에서 소수(234.3같은)를 float로 표기
            y = float(response["addresses"][0]["y"])
            print(title, address, category, show, episode, x, y)
            doc = {
                "title": title,
                "address": address,
                "category": category,
                "show": show,
                "episode": episode,
                "mapx": x,
                "mapy": y}
            db.matjips.insert_one(doc)
            # db 저장!
        else:
            print(title, "좌표를 찾지 못했습니다")