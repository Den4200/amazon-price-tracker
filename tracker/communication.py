import os
import sys

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

import settings

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

        content = open(os.path.join(sys.path[0], "templates", "price_drop_email.html"), "r").read().format(item_name=self.item_name, item_url=self.item_url, item_price=self.item_price, target_price=self.target_price)
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

            sms = open(os.path.join(sys.path[0], "templates", "price_drop_text.txt"), "r").read().format(item_url=self.item_url, item_price=self.item_price, target_price=self.target_price)
            self.msg.attach(MIMEText(sms, 'plain'))

            sms = self.msg.as_string()
            self.server.sendmail(settings.sender_email, self.findGateway(), sms)
            self.server.close()
