#!usr/bin/env python3
# -*- coding:utf-8 -*-
"""
    copyright:hualoushan
    date:2020-08-06
"""

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from time import sleep
import sqlite3
import time
from apscheduler.schedulers.blocking import BlockingScheduler
from chinese_calendar import is_workday, is_holiday
from datetime import datetime
import json
import requests
import os

G_PATH = "/home/app/web01/geckodriver.log"
# sqlite3记录 linux
SQLITE3_PATH = "/home/app/web01/isodb.db"
# sqlite3记录 windows
#SQLITE3_PATH = "C:\\lxx\\autologin\\kdal\\isodb.db"
# 日志
LOG_PATH = "/home/app/web01/error.log"
#LOG_PATH = "C:\\lxx\\autologin\\kdal\\error.log"
SUM = 0


# 数据库
class sqlrec():
    # 初始化数据表
    def __init__(self):
        sql = """create table if not exists isodb
                (systime text, isonum text, content text ,href text)
        """
        conn = sqlite3.connect(SQLITE3_PATH)
        c = conn.cursor()
        c.execute(sql)
        conn.commit()
        conn.close()
    # 插入操作
    def dosql(self, sql):
        conn = sqlite3.connect(SQLITE3_PATH)
        c = conn.cursor()
        c.execute(sql)
        conn.commit()
        conn.close()
    # 查询操作
    def selectsql(self, sql):
        conn = sqlite3.connect(SQLITE3_PATH)
        c = conn.cursor()
        c.execute(sql)
        selrec = c.fetchall()
        conn.close()
        return selrec

def spider_iso(iso_ver):
    try:
        global SUM
        db = sqlrec()
        # 无界面访问
        firefox_options = Options()
        firefox_options.set_headless()
        driver = webdriver.Firefox(firefox_options = firefox_options)
        url = "https://www.iso.org/search.html?q=" + iso_ver
        driver.get(url)
        sleep(3)
        find_mark = driver.find_elements_by_xpath("//div[contains(@id, 'search-results')]//\
            div[contains(@class, 'media-body')]/h6/a")
        count = 1
        for x in find_mark:
            sql = "select 1 from isodb where isonum = '" + str(iso_ver) + \
                "' and content = '" + str(x.get_attribute('title')) + "'"
            sel_iso = db.selectsql(sql)
            if sel_iso == []:
                systime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                content = x.get_attribute('title')
                href = x.get_attribute('href')
                sql = "insert into isodb(systime, isonum, content, href) \
                values('" + str(systime) + "', '" + str(iso_ver) + "', '"  + str(content) + "', '"  + str(href) + "')"
                db.dosql(sql)
                tsy1 = "重要提醒！！！ISO [" + iso_ver + "] 有更新" + '\n' + content + '\n' + href
                print(tsy1)
            count += 1
            if count > 1:
                break
        SUM += 1
        print(SUM)
        driver.close()
    except Exception as e:
        with open(LOG_PATH, 'a', encoding = 'utf-8') as f:
            f.write(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "  " +str(e) + '\n')

def job():
    iso_ver = ['9000', '9001', '13485', '22163', '19012-1', '19012-2', '19012-3', '18221',\
        '27911', '18337', '21073', '12233', '15739', '16505', '19084', '10993-12', '14971', '24971',\
            '8600-1', '8600-3', '8600-4', '8600-5', '8600-6', '10993-5', '17665-2', '17665-3']
    if os.path.exists(G_PATH):
        os.remove(G_PATH)
    if is_workday(datetime.now()):
        for x in iso_ver:
            spider_iso(x)
            sleep(2)

if __name__ == '__main__':
    # BlockingScheduler
    scheduler = BlockingScheduler()
    scheduler.add_job(job, "cron", day_of_week="mon-sun", hour = 14, minute = 51)
    #scheduler.add_job(job, "cron", day_of_week="mon", hour = 8, minute = 40)
    #scheduler.add_job(job2, "cron", day_of_week="mon-sun", hour = 17, minute = 1)
    #scheduler.add_job(job3, "cron", day='3rd fri', hour='9-11')
    #scheduler.add_job(job4, "interval", minutes = 1, start_date = "2020-7-23 09:30:00", end_date = "2020-7-23 09:40:00")
    #scheduler.add_job(job5, "cron", day_of_week="mon-sun", hour = '8, 12', minute = 30)
    #scheduler.add_job(job6, "cron", day_of_week="mon-sun", hour = '9, 11, 13, 15', minute = 30)
    scheduler.start()