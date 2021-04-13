import sys
import requests
import json
import schedule
from datetime import datetime
import time
from time import sleep
from time import gmtime, strftime

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from pathlib import Path
import smtplib

url = "https://www.devialet.com/zh-tw/true-wireless-earbuds/gemini/"

options = Options()
options.add_argument("--disable-notifications")

data_before = ""

def getSittingText():
    with open("config.json","r") as f:
        data_json = json.load(f)
    return data_json

def updatedSittingText(text):
    print("updateSittingText", text)
    data_json = getSittingText()
    data_json['text'] = text
    data_json['time'] = strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open("config.json","w") as f:
        json.dump(data_json, f) 

def postMail():
    print("Prepare to Post Mail ...")
    with open("sitting.json","r") as f:
        data_json = json.load(f)
    content = MIMEMultipart()  #建立MIMEMultipart物件
    content["subject"] = "[BREND - Server] Devialet Gemini 官方業面更新"  #郵件標題
    content["from"] = data_json['sender']['email']  #寄件者
    content["to"] = data_json['addressee']['email'] #收件者
    content.attach(MIMEText(data_before['text'] + "   - 更新時間" + data_before['time']))  #郵件內容
    content.attach(MIMEImage(Path("page.png").read_bytes()))
    with smtplib.SMTP(host=data_json['sender']['host'], port=data_json['sender']['port']) as smtp:  # 設定SMTP伺服器
        try:
            smtp.ehlo()  # 驗證SMTP伺服器
            smtp.starttls()  # 建立加密傳輸
            smtp.login(data_json['sender']['email'], data_json['sender']['key'])  # 登入寄件者gmail
            smtp.send_message(content)  # 寄送郵件
        except Exception as e:
            print("Error message: ", e)
        else:
            print("Mail post Complete!")

def getWebPagePhoto():
    driver = webdriver.Chrome('C:\\Tools\\chromedriver\\chromedriver.exe', chrome_options=options)
    driver.set_window_size(2160,2160)
    driver.get(url)
    
    try_c = 5
    try_time = 1
    while try_c > 0:
        try_c -= 1
        sleep(try_time)
        try:
            driver.find_element_by_xpath('//*[@id="onetrust-accept-btn-handler"]').click()
        finally: 
            print("ACCEPT ALL COOKIES - button try: " + str(try_c))
            break
    sleep(0.1)
    driver.save_screenshot('page.png')
    driver.close()

def checkPage():
    resp = requests.get(url)
    resp.encoding = 'utf-8'

    html_soup = BeautifulSoup(resp.text, 'html.parser')

    data = html_soup.select(".product__synthesis")
    # print(type(data[0].text), data[0].text)
    if (data_before['text'] != data[0].text):
        print("[" + strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "]", "網址資訊更新 - 開始更新並寄出資訊")
        data_before['text'] = str(data[0].text)
        updatedSittingText(data_before['text'])
        getWebPagePhoto()
        postMail()
    else:
        print("[" + strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "]","網址資訊尚未更新 - 等待5分鐘後更新更新")


schedule_time=5
data_before = getSittingText()
schedule.every(schedule_time).minutes.do(checkPage)


if __name__ == "__main__":

    # sys.exit()
    while True:
        schedule.run_pending()
        time.sleep(1)
    