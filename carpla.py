import dataclasses, logging
from utils.normalize import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from database.script.db import create_postgresql_uri, Manipulate
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from items import ItemTemplate


class CarplaCrawler:
    NAME = "carpla"

    def __init__(self):
        USER = 'newuser'
        PASSWORD = '123456'
        HOST = 'tcp.appengine.bfcplatform.vn'
        PORT = 23444
        DATABASE = 'car_price_form'
        self.STATE = "Đang bán"
        self.current_page = 0
        self.base_url = 'https://carpla.vn/mua-xe'
        self.driver = webdriver.Edge()
        self.driver.maximize_window()
        try:
            self.uri = create_postgresql_uri(USER, PASSWORD, HOST, PORT, DATABASE)
            self.db = Manipulate(url=self.uri)
        except:
            logging.error("Fail to connect Database")

    def get_url_list(self):
        self.driver.get(self.base_url)
        self.driver.implicitly_wait(4)
        while True:
            try:
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH,"//button[@class='btn-highlight font-bold !px-8 text-xl w-[200px] p-button p-component']")))
                button = self.driver.find_element(By.XPATH,"//button[@class='btn-highlight font-bold !px-8 text-xl w-[200px] p-button p-component']")
                self.driver.execute_script("arguments[0].click();", button)
            except:
                break
        url_list = []
        soup = BeautifulSoup(self.driver.page_source, 'html.parser').findAll("div", class_="rounded-xl product-card cursor-pointer relative w-full")
        for i, tag in enumerate(soup):
            state = tag.find("div", class_="tag-status deposited drop-shadow-lg absolute z-10 text-sm flex top-4 py-1 rounded-tl-lg px-2 rounded-tr-lg rounded-br-lg text-white bg-cyan-600").get_text().strip()
            if state == self.STATE:
                url_list.append("https://carpla.vn" + tag.find("a")["href"])
        self.driver.close()
        return url_list

    def start_crawl(self):
        url_list = self.get_url_list()
        self.driver = webdriver.Edge()
        self.driver.maximize_window()

        for car_url in url_list:
            try:
                car_info = dataclasses.asdict(self.parse_car(car_url))
                self.db.add_new_car(**car_info)
                print("Them xe thanh cong")
            except:
                logging.error("Crawl fail at", car_url, "object: ", car_info)

    def parse_car(self, url):
        self.driver.get(url)
        self.driver.implicitly_wait(7)
        general_info = self.driver.find_element(By.XPATH, "//div[@class='col-span-12 xl:col-span-4 xl:pl-2']")

        title = general_info.find_element(By.XPATH, "//h1[@class='text-lg font-bold line-clamp-2']").text.split()
        raw_brandname = title[0]
        raw_version = " ".join(title[1:-1])
        raw_price = normalize_str_to_int(general_info.find_element(By.XPATH, "//div[@class='xl:text-3xl text-2xl price']").find_element(By.TAG_NAME, "span").text)
        raw_city = general_info.find_element(By.XPATH, "//div[@class='text-stone-600 py-2']").find_element(By.XPATH, "//div[@class='pr-3 flex items-baseline']").find_element(By.XPATH, "//span[@class='px-1 text-neutral-700 text-sm line-clamp-1']").text

        _ = [i.text for i in self.driver.find_elements(By.XPATH, "//span[@class='text-gradient-primary font-bold text-xl']")]
        raw_year = int(_[1])
        raw_distance = normalize_str_to_int(_[2])
        raw_transmission = _[3]

        _ = self.driver.find_elements(By.XPATH,"//span[@class='font-bold pl-8']")
        raw_fuel = _[0].text
        raw_origin = _[5].text
        raw_drive = _[2].text

        return ItemTemplate(brandname=raw_brandname,
                            version=raw_version,
                            transmission=raw_transmission,
                            fuel=raw_fuel,
                            origin=raw_origin,
                            year=raw_year,
                            distance=raw_distance,
                            city=raw_city,
                            price=raw_price,
                            drive=raw_drive)

if __name__ == "__main__":
    pass