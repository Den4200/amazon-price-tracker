# Settings

import os
import sys

# Search "my user agent" on Google to find user agent
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'


# Time interval in seconds for when the tracker checks prices
check_interval = 1800


# Email address in which the tracker will use to send a message (Must be a gmail account)
# This is required!
sender_email = ''


# Password of the sender email address (Edit the sender_password.key file to change the password)
# This is required!
with open(os.path.join(sys.path[0], "sender_password.key"), "r") as f:
    sender_password = f.read()


# Email address in which the tracker will send a message to
# This is required!
reciever_email = ''


# Phone number in which the tracker will send a message to (Do not include dashes or any extra characters!)
# Leave '' if no text is desired
reciever_phone_number = ''


# Cell provider for the phone number ('at&t', 'verizon', or 'tmobile')
# Leave '' if no phone number is given
reciever_cell_provider = ''
