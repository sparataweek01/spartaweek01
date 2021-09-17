from selenium import webdriver
from bs4 import BeautifulSoup
import time
from selenium.common.exceptions import NoSuchElementException
from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import requests

client = MongoClient('3.34.5.163', 27017, username="test", password="test")
db = client.dbsparta_plus_week4

result1 = list(db.recipes.find({'title': {"$regex": "종원"}}))
result2 = list(db.recipes.find({'title2': {"$regex": "종원"}}))
result3 = list(db.recipes.find({'title3': {"$regex": "종원"}}))

result4 = result1 + result2 + result3

for result in result4:
    db.test.save(result)




