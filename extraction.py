import cv2
from PIL import Image
import easyocr
import sqlite3 as sql
import pandas as pd
import os
import matplotlib.pyplot as plt
import re
from main import data

con=sql.connect('cards.db')
cur=con.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS card_data
                   (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_name TEXT,
                    card_holder TEXT,
                    designation TEXT,
                    mobile_number VARCHAR(50),
                    email TEXT,
                    website TEXT,
                    area TEXT,
                    city TEXT,
                    state TEXT,
                    pin_code VARCHAR(10),
                    image LONGBLOB
                    )''')
con.commit()

read = easyocr.Reader(['en'])
white=Image.open('white.jpg')

def save_card(uploaded_card):
    cards_dir = os.path.join(os.getcwd(), "saved_cards")
    with open(os.path.join(cards_dir, uploaded_card.name), "wb") as f:
        f.write(uploaded_card.getbuffer())

def preview(image, result,):
    for (box, text, p) in result:
        (t1, t2, b2, b1) = box
        t1 = (int(t1[0]), int(t1[1]))
        t2 = (int(t2[0]), int(t2[1]))
        b2 = (int(b2[0]), int(b2[1]))
        b1 = (int(b1[0]), int(b1[1]))
        cv2.rectangle(image, t1, b2, (0, 255, 0), 2)
        cv2.putText(image, text, (t1[0], t1[1] - 10),
        cv2.FONT_ITALIC, 0.7, (0, 255, 0), 2)
    plt.rcParams['figure.figsize'] = (15, 15)
    plt.axis('off')
    plt.imshow(image)


def get_data(res):
    for j, i in enumerate(res):

        #WEBSITE_URL
        if "www " in i.lower() or "www." in i.lower():
            data["website"].append(i)
        elif "WWW" in i:
            data["website"] = res[4] + "." + res[5]

        #EMAIL
        elif "@" in i:
            data["email"].append(i)

        # To get MOBILE NUMBER
        elif "-" in i:
            data["mobile_number"].append(i)
            if len(data["mobile_number"]) == 2:
                data["mobile_number"] = " & ".join(data["mobile_number"])

        #COMPANY NAME
        elif j == len(res) - 1:
            data["company_name"].append(i)

        #CARD HOLDER NAME
        elif j == 0:
            data["card_holder"].append(i)

        #DESIGNATION
        elif j == 1:
            data["designation"].append(i)

        #AREA
        if re.findall('^[0-9].+, [a-zA-Z]+', i):
            data["area"].append(i.split(',')[0])
        elif re.findall('[0-9] [a-zA-Z]+', i):
            data["area"].append(i)

        # CITY NAME
        match1 = re.findall('.+St , ([a-zA-Z]+).+', i)
        match2 = re.findall('.+St,, ([a-zA-Z]+).+', i)
        match3 = re.findall('^[E].*', i)
        if match1:
            data["city"].append(match1[0])
        elif match2:
            data["city"].append(match2[0])
        elif match3:
            data["city"].append(match3[0])

        #STATE
        state_match = re.findall('[a-zA-Z]{9} +[0-9]', i)
        if state_match:
            data["state"].append(i[:9])
        elif re.findall('^[0-9].+, ([a-zA-Z]+);', i):
            data["state"].append(i.split()[-1])
        if len(data["state"]) == 2:
            data["state"].pop(0)

        #PINCODE
        if len(i) >= 6 and i.isdigit():
            data["pin_code"].append(i)
        elif re.findall('[a-zA-Z]{9} +[0-9]', i):
            data["pin_code"].append(i[10:])

def send_db(con,df):
    df.to_sql('card_data',con,if_exists='append')

