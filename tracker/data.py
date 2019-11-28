import os
import sys
import csv

import requests
from bs4 import BeautifulSoup

import settings
from settings import CSV_ITEM_FILE, ITEM_NUM_FILE


class ItemData():

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
        asin_start = self.URL.find('B0')
        simple_url = f'https://www.amzn.com/dp/{self.URL[asin_start:asin_start+10]}'
        return simple_url

    def minusOneItemNum(self):
        with open(ITEM_NUM_FILE, 'r') as f:
            prev_num = f.read()
            
        with open(ITEM_NUM_FILE, 'w') as f:
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
        with open(CSV_ITEM_FILE, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            
            for line in csv_reader:  
                
                if self.findSimpleUrl() in line[0]:
                    return True

    def itemFileName(self):
        with open(ITEM_NUM_FILE, 'r') as f:
            prev_num = f.read()
        
        with open(ITEM_NUM_FILE, 'w') as f:
            new_num = int(prev_num) + 1
            f.write(str(new_num))
        
        name = self.preTitle().strip().replace(',', '')[:20] + '{' + str(new_num) + '}'
        csv_name = f'{name}.csv'
        png_name = f'{name}.png'
        return csv_name, png_name

    def newFile(self, target_price):        
        csv_name, png_name = self.itemFileName()
        
        try:
            with open(CSV_ITEM_FILE, 'a') as f:
                f.write(f'{self.findSimpleUrl()},{csv_name},{png_name},{float(target_price)}\n')
        except Exception:
            self.minusOneItemNum()
            print('Not a valid target price! Do not use a $ sign')
            exit()

    def delFile(self):
        url = self.findSimpleUrl()
        temp_csv = os.path.join(sys.path[0], 'data', 'temp_data.csv')

        with open(CSV_ITEM_FILE, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            
            for line in csv_reader:

                if url == line[0]:

                    with open(temp_csv, 'w') as copier:
                        csv_file.seek(0)

                        for line in csv_reader:
                            if url != line[0]:
                                copier.write(f"{','.join(line)}\n")

        os.remove(CSV_ITEM_FILE)
        os.rename(temp_csv, CSV_ITEM_FILE)

        return True

    def findFile(self):
        with open(CSV_ITEM_FILE, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            
            for line in csv_reader:    
                if self.findSimpleUrl() == line[0]:
                    return line[1]

    def findPng(self):
        with open(CSV_ITEM_FILE, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            
            for line in csv_reader:    
                if self.findSimpleUrl() == line[0]:
                    return line[2]

    def findTargetPrice(self):
        with open(CSV_ITEM_FILE, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            
            for line in csv_reader:
                if self.findSimpleUrl() == line[0]:
                    return line[3]

    def filesNames(self):
        csv_item_spec_file = os.path.join(sys.path[0], 'item-csv', self.findFile())
        item_png = os.path.join(sys.path[0], 'graphs', self.findPng())
        return [csv_item_spec_file, item_png]

    def save(self):
        if self.doesExist() == True:
            return 'already_exists'
        else:
            target_price = input('Target price for new item: ')
            self.newFile(target_price)
            
            return 'newItem_sucess'
