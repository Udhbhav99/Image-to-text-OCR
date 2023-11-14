import pandas as pd
from extraction import *
import streamlit as st
from PIL import Image
import re
import os
from streamlit_option_menu import option_menu
icon= Image.open('62780.png')

st.set_page_config(page_title='Extracting Data From Biz Cards', page_icon=icon,layout='wide')
st.markdown(f""" <style>.stApp {{
                    background:url("https://img.freepik.com/free-photo/abstract-textured-backgound_1258-30436.jpg?w=740&t=st=1699907290~exp=1699907890~hmac=81b886ae2a3b31345e3d203a63f8c415376ba3f0498378bddcc49c78a9c1753d");
                    background-size: cover}}
                 </style>""", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: white;'>Extracting Business Card Data</h1>",
            unsafe_allow_html=True)

option=option_menu(None,["HOME","EXTRACT DATA","MODIFY DATA"],
                   icons=[":house:",":floppy_disk:",":file_folder:"],orientation="horizontal",
                   styles={"nav-link": {"font-size": "30px", "text-align": "centre", "margin": "-2px",
                                        "--hover-color": "red"},
                           "icon": {"font-size": "30px"},
                           "container" : {"max-width": "5000px","background-color": "black"},
                           "nav-link-selected": {"background-color": "#1fe609"}})
if option=='HOME':
    st.header('About')
    st.divider()
    st.write('This tool helps extract data from images of business cards and store them into a database.'
             'This data can further be modifies if any changes are required or can be deleted from the database')
    st.header('Working')
    st.divider()
    st.write("Easyocr is used to read text from image and is stored into a Dataframe"
             "The dataframe sends data into a database and this is used to modify the data")

elif option=='EXTRACT DATA':
    if st.button("View Data"):
        cur.execute(
            "select company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code from card_data")
        updated_df = pd.DataFrame(cur.fetchall(),
                                  columns=["Company_Name", "Card_Holder", "Designation", "Mobile_Number",
                                           "Email",
                                           "Website", "Area", "City", "State", "Pin_Code"])
        st.write(updated_df)
    st.subheader("Upload the Card")
    uploaded_card = st.file_uploader("upload", label_visibility="collapsed", type=["png", "jpeg", "jpg"])

    if uploaded_card is not None:
        save_card(uploaded_card)

        c1,c2=st.columns([1,1])
        with c1:
            st.markdown('')
            st.markdown('')
            st.markdown('##UPLOADED CARD')
        with c2:
            st.markdown('')
            st.markdown('')
            with st.spinner('processing...'):
                st.set_option('deprecation.showPyplotGlobalUse', False)
                saved_img = os.getcwd() + "\\" + "saved_cards" + "\\" + uploaded_card.name
                img=cv2.imread(saved_img)
                res = read.readtext(saved_img)
                st.markdown("### Processed image")
                st.pyplot(preview(img, res))

        img = os.getcwd() + "\\" + "saved_cards" + "\\" + uploaded_card.name
        result = read.readtext(saved_img, detail=0, paragraph=False)


    def binary(file):
        with open(file, 'rb') as file:
            binary_data = file.read()
        return binary_data


    data = {"company_name": [],
            "card_holder": [],
            "designation": [],
            "mobile_number": [],
            "email": [],
            "website": [],
            "area": [],
            "city": [],
            "state": [],
            "pin_code": [],
            "image": binary(saved_img)
            }

    get_data(result)

    df=pd.DataFrame(data)
    st.write('Extracted data')
    st.dataframe(df)
    if st.button('UPLOAD'):
        send_db(con,df)
        st.success("### Upload successful!")
elif option=='MODIFY DATA':
    st.write(':red[you can view modify or delete data here]')
    st.markdown('')
    st.markdown('')
    st.markdown('')
    update=option_menu(None,options=["modify","delete"], orientation='horizontal',
                        styles = {"container": {"width": "100%"},
                                  "nav-link": {"font-size": "20px", "text-align": "center", "margin": "-2px"},
                                  "nav-link-selected": {"background-color": "black"}})
    if update=='modify':
        try:
            cards={}
            cur.execute("select card_holder from car_data")
            names=cur.fetchall()
            for i in names:
                cards[i[0]]=i[0]
            card_options=['--select--']+list(cards.keys())
            selected_card=st.selectbox('select a card',card_options)
            if selected_card=='--select--':
                st.write('NO CARD SELECTED')
            else:
                cur.execute(f"select company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code from card_data WHERE card_holder={selected_card}")
                result = cur.fetchone()


                company_name = st.text_input("Company_Name", result[0])
                card_holder = st.text_input("Card_Holder", result[1])
                designation = st.text_input("Designation", result[2])
                mobile_number = st.text_input("Mobile_Number", result[3])
                email = st.text_input("Email", result[4])
                website = st.text_input("Website", result[5])
                area = st.text_input("Area", result[6])
                city = st.text_input("City", result[7])
                state = st.text_input("State", result[8])
                pin_code = st.text_input("Pin_Code", result[9])

                cur.execute(f"update card_data set company_name={company_name},card_holder={card_holder},designation={designation},mobile_number={mobile_number},email={email},website={website},area={area},city={city},state={state},pin_code={pin_code} where card_holder=%s")
                con.commit()
                st.success("Updated successfully.")
            if st.button("View Data"):
                cur.execute(
                    "select company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code from card_data")
                updated_df = pd.DataFrame(cur.fetchall(),
                                          columns=["Company_Name", "Card_Holder", "Designation", "Mobile_Number",
                                                   "Email",
                                                       "Website", "Area", "City", "State", "Pin_Code"])

                st.dataframe(updated_df)
        except:
            st.warning("There is no data available in the database")

    if update=='delete':
        try:
            cards = {}
            cur.execute("select card_holder from car_data")
            names = cur.fetchall()
            for i in names:
                cards[i[0]] = i[0]
            card_options = ['--select--'] + list(cards.keys())
            selected_card = st.selectbox('select a card', card_options)
            if selected_card == '--select--':
                st.write('NO CARD SELECTED')
            else:
                st.write(f'selected card is: {selected_card}')
                if st.button('yes proceed'):
                    cur.execute(f"DELETE FROM card_data WHERE card_holder={selected_card}")
                    con.commit()
            if st.button("View Data"):
                cur.execute(
                    "select company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code from card_data")
                updated_df = pd.DataFrame(cur.fetchall(),
                                          columns=["Company_Name", "Card_Holder", "Designation", "Mobile_Number",
                                                   "Email",
                                                   "Website", "Area", "City", "State", "Pin_Code"])

                st.dataframe(updated_df)
        except:









