from selenium import webdriver
from bs4 import BeautifulSoup
import time
from selenium.common.exceptions import NoSuchElementException
from pymongo import MongoClient
import requests

client = MongoClient('13.209.85.240', 27017, username="test", password="test")
db = client.db_hh_w1_g31


url = "https://www.10000recipe.com/ranking/home_new.html"

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get(url, headers=headers)

# driver.get(url)
# time.sleep(2)

soup = BeautifulSoup(data.text, 'html.parser')
#contents_area_full > div > ul.common_sp_list_ul.ea4 > li:nth-child(1)

recipes = soup.select('#contents_area_full > div > ul.common_sp_list_ul.ea4 > li')


for recipe in recipes:
    title = recipe.select_one('div.common_sp_caption > div.common_sp_caption_tit.line2').text
    view = recipe.select_one('div.common_sp_caption > div.common_sp_caption_rv > span.common_sp_caption_buyer').text #조회수 숫자 뗴기
    img = recipe.select_one('div.common_sp_thumb > a > img')['src']
    user = recipe.select_one('div.common_sp_caption > div.common_sp_caption_rv_name > a').text
    url = recipe.select_one('div.common_sp_thumb > a')['href']



    if recipe.select_one('div.common_sp_caption > div.common_sp_caption_rv > span.common_sp_caption_rv_ea') is not None:
        doc = {
                    'title': title,
                    'ingredients': "",
                    'process': "",
                    'time': "",
                    'cost': "",
                    'subtitle': "",
                    'category': "",
                    'hashtag': "",
                    'recipe_img': "",
                    'recipe_img_real': "",
                    'upload_user': user,
                    'view': view,
                    'img-url': img,
                    'review': recipe.select_one('div.common_sp_caption > div.common_sp_caption_rv > span.common_sp_caption_rv_ea').text,
                    'url': 'https://www.10000recipe.com'+url
                }
    else:
        doc = {

            'title': title,
            'ingredients': "",
            'process': "",
            'time': "",
            'cost': "",
            'subtitle': "",
            'category': "",
            'hashtag': "",
            'recipe_img': "",
            'recipe_img_real': "",
            'upload_user': user,
            'view': view,
            'img-url': img,
            'review': "(0)",
            'url': 'https://www.10000recipe.com' + url

        }
    print(doc['url'])

    db.recipes.insert_one(doc)