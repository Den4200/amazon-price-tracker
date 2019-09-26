import requests
import time
from bs4 import BeautifulSoup

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style
from matplotlib.pyplot import figure, close

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

import csv

import multiprocessing

import settings

class itemData():

    def __init__(self, URL):
        try:
            page = requests.get(URL, headers={"User-Agent": settings.user_agent})
            soup0 = BeautifulSoup(page.content, "html.parser")
            soup = BeautifulSoup(soup0.prettify(), "html.parser")
            
            self.soup = soup
        except Exception:
            print('Invalid URL!')
            exit()

        self.URL = URL

    def findSimpleUrl(self):
        ASIN_start = self.URL.find('B0')
        simple_url = f'https://www.amzn.com/dp/{self.URL[ASIN_start:ASIN_start+10]}'
        return simple_url

    def minusOneItemNum(self):
        itemNum_file = os.path.join(sys.path[0], "itemNum.txt")

        with open(itemNum_file, 'r') as f:
            prev_num = f.read()
            
        with open(itemNum_file, 'w') as f:
            new_num = int(prev_num) - 1
            f.write(str(new_num))

    def preTitle(self):
        try:
            productTitle = self.soup.find(id="productTitle").get_text()
            return productTitle
        except Exception:
            self.minusOneItemNum()
            print('Invalid URL!')
            exit()
    
    def doesExist(self):
        csv_item_file = os.path.join(sys.path[0], "data.csv")

        with open(csv_item_file, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            
            for line in csv_reader:  
                
                if self.findSimpleUrl() in line[0]:
                    return True

    def itemFileName(self):
        itemNum_file = os.path.join(sys.path[0], "itemNum.txt")

        with open(itemNum_file, 'r') as f:
            prev_num = f.read()
        
        with open(itemNum_file, 'w') as f:
            new_num = int(prev_num) + 1
            f.write(str(new_num))
        
        csv_name = self.preTitle().strip()[:20] + '{' + str(new_num) + '}.csv'
        png_name = self.preTitle().strip()[:20] + '{' + str(new_num) + '}.png'
        return csv_name, png_name

    def newFile(self, target_price):
        csv_item_file = os.path.join(sys.path[0], "data.csv")
        
        csv_name, png_name = self.itemFileName()
        
        try:
            with open(csv_item_file, 'a') as f:
                f.write(f'{self.findSimpleUrl()},{csv_name},{png_name},{float(target_price)}\n')
        except Exception:
            self.minusOneItemNum()
            print('Not a valid target price! Do not use a $ sign')
            exit()

    def findFile(self):
        csv_item_file = os.path.join(sys.path[0], "data.csv")

        with open(csv_item_file, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            
            for line in csv_reader:    
                
                if self.findSimpleUrl() == line[0]:
                    return line[1]

    def findPng(self):
        csv_item_file = os.path.join(sys.path[0], "data.csv")

        with open(csv_item_file, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            
            for line in csv_reader:    

                if self.findSimpleUrl() == line[0]:
                    return line[2]

    def findTargetPrice(self):
        csv_item_file = os.path.join(sys.path[0], "data.csv")

        with open(csv_item_file, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            
            for line in csv_reader:    

                if self.findSimpleUrl() == line[0]:
                    return line[3]

    def filesNames(self):
        csv_item_spec_file = os.path.join(sys.path[0], 'item-csv\\' + self.findFile())
        item_png = os.path.join(sys.path[0], 'graphs\\' + self.findPng())
        return [csv_item_spec_file, item_png]

    def save(self):
        if self.doesExist() == True:
            return 'already_exists'
        else:
            target_price = input('Target price for new item: ')
            self.newFile(target_price)
            
            return 'newItem_sucess'

class Tracker(itemData):
    
    def __init__(self, URL):
        page = requests.get(URL, headers={"User-Agent": settings.user_agent})
        soup0 = BeautifulSoup(page.content, "html.parser")
        soup = BeautifulSoup(soup0.prettify(), "html.parser")

        self.URL = URL
        self.soup = soup
        self.target_price = self.findTargetPrice()

    def title(self):
        productTitle = self.soup.find(id="productTitle").get_text()
        return productTitle

    def price(self): 
        try:
            productPrice = self.soup.find(id="priceblock_ourprice").get_text()
            return productPrice

        except AttributeError:

            try:
                productPrice = self.soup.find(id="priceblock_dealprice").get_text()
                return productPrice

            except AttributeError:
                pass

    def int_price(self):
        try:
            chars = len(self.price())
            return float(self.price()[1:chars])
        
        except TypeError:
            pass

    def compare_prices(self):
        try:
            if self.int_price() <= float(self.target_price):
                return 'below'
            elif self.int_price() >= float(self.target_price):
                return 'above'
        
        except Exception:
            return 'out-of-stock'

    def graph(self):
        csv_file, png_file = self.filesNames()

        try:
            with open(csv_file, "a") as f:
                f.write(f"{int(time.time() - 14400)}, {self.int_price()}, {self.target_price}\n")

            figure(num=None, figsize=(9, 6), dpi=120, facecolor='w', edgecolor='k')

            plt.clf()

            df = pd.read_csv(csv_file, names=['Time', 'Price', 'Target Price'])
            df['Date'] = pd.to_datetime(df['Time'],unit='s')
            df.drop("Time", 1,  inplace=True)
            df.set_index("Date", inplace=True)

            df['Price'].plot()
            df['Target Price'].plot()

            plt.legend()

            plt.savefig(png_file)  
            close()

        except Exception:
            pass

class Communication:
    
    def __init__(self, item_name, item_url, item_price, target_price):
        self.item_name = item_name
        self.item_url = item_url
        self.item_price = item_price
        self.target_price = target_price

        server = smtplib.SMTP('smtp.gmail.com', 587)

        server.ehlo()
        server.starttls()
        server.login(settings.sender_email, settings.sender_password)

        self.server = server

        msg = MIMEMultipart()
        msg['From'] = settings.sender_email

        self.msg = msg

    def findGateway(self):

        if settings.reciever_cell_provider == 'at&t':
            sms_gateway = settings.reciever_phone_number + '@txt.att.net'
            return sms_gateway

        elif settings.reciever_cell_provider == 'verizon':
            sms_gateway = settings.reciever_phone_number + '@vtext.com'
            return sms_gateway

        elif settings.reciever_cell_provider == 'tmobile':
            sms_gateway = settings.reciever_phone_number + '@tmomail.net'
            return sms_gateway

        else:
            print('Error! Your cell provider is not supported.')
            exit()

    def sendEmail(self):
        self.msg['To'] = settings.reciever_email
        self.msg['Subject'] = f'Price drop on {self.item_name}!'

        content = open(os.path.join(sys.path[0], "price_drop_email.html"), "r").read().format(item_name=self.item_name, item_url=self.item_url, item_price=self.item_price, target_price=self.target_price)
        self.msg.attach(MIMEText(content, 'html'))

        content = self.msg.as_string()
        self.server.sendmail(settings.sender_email, settings.reciever_email, content)
        self.server.close()

    def sendText(self):
        if settings.reciever_cell_provider == '' or settings.reciever_phone_number == '':
            print('No text has been sent. A phone number and/or cell provider has not been set.')

        else:
            self.__init__(self.item_name, self.item_url, self.item_price, self.target_price)

            self.msg['To'] = self.findGateway()

            sms = open(os.path.join(sys.path[0], "price_drop_text.txt"), "r").read().format(item_url=self.item_url, item_price=self.item_price, target_price=self.target_price)
            self.msg.attach(MIMEText(sms, 'plain'))

            sms = self.msg.as_string()
            self.server.sendmail(settings.sender_email, self.findGateway(), sms)
            self.server.close()


def listItems():
    csv_item_file = os.path.join(sys.path[0], "data.csv")

    items = []

    with open(csv_item_file, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)

        for line in csv_reader:
            items.append(line[1][:20] + ': ' + line[0])
        
    return items

def trackerInstance(URL):
    item = Tracker(URL)

    style.use("fivethirtyeight")
    item.graph()

    if item.compare_prices() == 'below':
        print(f'{item.price()} < ${item.target_price}\n')
        comms = Communication(item.title().strip(), URL, item.price(), '$' + item.target_price)
        
        comms.sendEmail()
        comms.sendText()

    elif item.compare_prices() == 'above':
        print(f'{item.price()} > ${item.target_price}\n')

    elif item.compare_prices() == 'out-of-stock':
        print(f'{item.price()} > ${item.target_price} - Item is out of stock\n')

def trackerLoop():
    while True:

        p = multiprocessing.Pool()
        URLs = []

        try:
            csv_item_file = os.path.join(sys.path[0], "data.csv")

            with open(csv_item_file, 'r') as csv_file:
                csv_reader = csv.reader(csv_file)

                for line in csv_reader:
                    
                    URL = line[0]

                    URLs.append(URL)
                    
            p.map(trackerInstance, URLs)
            p.close()

            time.sleep(settings.check_interval)
        except Exception as e:
            print(e, '\nError! Trying again in 30 seconds..')
            time.sleep(30)
            continue

def addItem():
    URL = input('Item URL: ')
    item = Tracker(URL)

    if itemData(URL).save() == 'already_exists':
        print('Item is already being tracked!')

    else:
        print(f'\n{item.title().strip()} has been added to the tracking list!')

def mainLoop():
    while True:
        option = input("""
        --------------------------------------------
        | Amazon Price Tracker v3.1 by Dennis Pham |
        |                                          |
        | 1. Run tracker                           |
        | 2. Add new item                          |
        | 3. List items                            |
        | 4. Exit                                  |
        |                                          |
        --------------------------------------------
        
             Option: """)                             

        if option == '1':
            trackerLoop()

        elif option == '2':
            addItem()

        elif option == '3':
            for item in listItems():
                print(item)

        elif option == '4':
            exit()
        
        else:
            print('This is not an option!')
            continue

if __name__ == "__main__":
    mainLoop()