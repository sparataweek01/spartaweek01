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
time.sleep(2)

for i in range(5):
    try:
        btn_more = driver.find_element_by_css_selector('#foodstar-front-location-curation-more-self > div > button')
        btn_more.click()
        time.sleep(2)
    except NoSuchElementException:
        break

req = driver.page_source
driver.quit()

soup = BeautifulSoup(req, 'html.parser')

places = soup.select('ul.restaurant_list > div > div > li > div > a')

for place in places:
    title = place.select_one("strong.box_module_title").text
    address = place.select_one("div.box_module_cont > div > div > div.mil_inner_spot > span.il_text").text
    subtitle = place.select_one("div.box_module_cont > div > span").text
    category = place.select_one("div.box_module_cont > div > div > div.mil_inner_kind > span.il_text").text
    show, episode = place.select_one("div.box_module_cont > div > div > div.mil_inner_tv > span.il_text").text.rsplit(
        " ", 1)
    img = place.select_one('div.box_module_image_w > img')['src']

    headers = {
        "X-NCP-APIGW-API-KEY-ID": "cegbwlugpl",
        "X-NCP-APIGW-API-KEY": "axxLfb4tsDvWrqDV4k4hpSMsGZF3l3MAp9sX94BA"
    }

    r = requests.get(f"https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode?query={address}", headers=headers)
    response = r.json()

    if response["status"] == "OK":
        if len(response["addresses"]) > 0:
            x = float(response["addresses"][0]["x"])
            # float("127.4") -> 127.4 문자열 -> 숫자로 바꿔줌
            y = float(response["addresses"][0]["y"])
            print(title, address, category, show, episode, x, y, img)

            doc = {
                "title": title,
                "address": address,
                "category": category,
                'img-url': img,
                "show": show,
                "episode": episode,
                "mapx": x,
                "mapy": y
            }
            db.matjips.insert_one(doc)

        else:
            print(title, "좌표를 찾지 못했습니다")




