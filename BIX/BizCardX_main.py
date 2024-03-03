#Importing Necessary Packages
import streamlit as st
import easyocr
import mysql.connector as sql_db
import pandas as pd
import re
from streamlit_option_menu import option_menu
import os
from PIL import Image


#StreamLit Part
#Setting Page 
icon = Image.open("OCRLogo.jpg")
st.set_page_config(page_title= "BizCardX: Extracting Business Card Data with OCR",
                   page_icon= icon,
                   layout= "wide",
                   initial_sidebar_state= "expanded",)

#Creating Options Menu 
selected = option_menu(None,["Home", "Extract and Upload", "Modify or Delete"],
                        icons=["house", "upload", "pencil"],
                        orientation="horizontal",
                        default_index=0,
                        styles={"nav-link": {"font-size": "20px", "text-align": "centre", "margin": "0px","---hover-color": "#6495ED"},
                                "icon": {"font-size": "35px"},
                                "container" : {"max-width": "6000px"},"nav-link-selected": {"background-color": "#0C86C8"}})

#Initializing EasyOCR
reader = easyocr.Reader(['en'], gpu=False)

#Create Dataframes from SQL
#MySQL Connection
mydb = sql_db.connect(host="localhost",
                   user="root",
                   password="#Saravanan27",
                   database= "bizcard_db",
                   auth_plugin='mysql_native_password'
                  )
mycursor = mydb.cursor(buffered=True)

# Create a table in the database
mycursor.execute("""
        CREATE TABLE IF NOT EXISTS business_card_data (
        id INTEGER PRIMARY KEY AUTO_INCREMENT,
        name VARCHAR(255),
        designation VARCHAR(255),
        company VARCHAR(255),
        email VARCHAR(255),
        website VARCHAR(255),
        primary_no VARCHAR(255),
        secondary_no VARCHAR(255),
        address TEXT,
        pincode INT
    )
    """)    
mydb.commit()

#Menu - Home Page  
if selected == 'Home':
    icon = Image.open("BizIcon.jpg")
    new_width = 1000
    new_height = 500
    resized_icon = icon.resize((new_width, new_height))
    st.image(resized_icon)
    
    st.markdown("# :green[BizCard - Business Card Data Extraction]")
    st.markdown(
        "### :green[Technologies used :]  Python, EasyOCR, MySQL, pandas, Streamlit.")
    st.markdown(
        "### :green[About :] Bizcard is a python application designed to extract information from business cards.")
    st.write()
    st.markdown("### The main purpose of Bizcard is to automate the process of extracting key details from business card images, such as name, designation, company, contact information, and other relevant data. By leveraging the power of OCR (Optical Character Recognition) provided by EasyOCR, Bizcard is able to extract text from the image")

#Menu - Extract and Upload Page
elif selected == "Extract and Upload":
    st.markdown("### Upload a Business Card")
    uploaded_file = st.file_uploader("upload here",label_visibility="collapsed",type=["jpg", "jpeg", "png"])

    if uploaded_file != None:
        image = uploaded_file.read()

        col1, col2, col3 = st.columns([1,1,2])
        with col3:
            # DISPLAYING THE UPLOADED CARD
            st.image(image)

        with col1:
            saved_img = os.getcwd()+ "\\" + "Cards"+ "\\"+ uploaded_file.name
            result = reader.readtext(saved_img,detail = 0,paragraph=False)

        data = {"card_holder" : [],
        "designation" : [],
        "company_name" : [],
        "email" : [],
        "mobile_number" :[], 
        "website" : [],
        "area" : [],
        "city" : [],
        "state" : [],
        "pin_code" : [],
        }    

        def get_data(result):
            for ind,i in enumerate(result):
                
                # To get WEBSITE_URL
                if "www " in i.lower() or "www." in i.lower():
                        data["website"].append(i)
                elif "WWW" in i:
                        data["website"] = result[4] +"." + result[5]

                # To get EMAIL ID
                elif "@" in i:
                        data["email"].append(i)

                # To get MOBILE NUMBER
                elif "-" in i:
                        data["mobile_number"].append(i)
                        if len(data["mobile_number"]) ==2:
                                data["mobile_number"] = " & ".join(data["mobile_number"])
                            
                elif ind == len(result) -1:
                        data["company_name"].append(i)       

                # To get CARD HOLDER NAME
                elif ind == 0:
                    data["card_holder"].append(i)

                # To get DESIGNATION
                elif ind == 1:
                        data["designation"].append(i)

                # To get AREA
                if re.findall('^[0-9].+, [a-zA-Z]+',i):
                        data["area"].append(i.split(',')[0])
                elif re.findall('[0-9] [a-zA-Z]+',i):
                        data["area"].append(i)

                # To get CITY NAME
                match1 = re.findall('.+St , ([a-zA-Z]+).+', i)
                match2 = re.findall('.+St,, ([a-zA-Z]+).+', i)
                match3 = re.findall('^[E].*',i)
                if match1:
                        data["city"].append(match1[0])
                elif match2:
                        data["city"].append(match2[0])
                elif match3:
                        data["city"].append(match3[0])

                # To get STATE
                state_match = re.findall('[a-zA-Z]{9} +[0-9]',i)
                if state_match:
                        data["state"].append(i[:9])
                elif re.findall('^[0-9].+, ([a-zA-Z]+);',i):
                        data["state"].append(i.split()[-1])
                if len(data["state"])== 2:
                        data["state"].pop(0)        

                # To get PINCODE        
                if len(i)>=6 and i.isdigit():
                        data["pin_code"].append(i)
                elif re.findall('[a-zA-Z]{9} +[0-9]',i):
                        data["pin_code"].append(i[10:])
        get_data(result)

        #Converting into DataFrame
        def create_df(data):
                    df = pd.DataFrame(data)
                    return df
        df = create_df(data)
        st.success("### Data Extracted!")
        st.table(df)

        a = st.button("upload to database")
        if a:
            for i,row in df.iterrows():
            #here %S means string values 
                    sql = """INSERT INTO business_card_data(card_holder,designation,company_name,email,mobile_number,website,area,city,state,pin_code)
                                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                    mycursor.execute(sql, tuple(row))
                    # the connection is not auto committed by default, so we must commit to save our changes
                    mydb.commit()
                    st.success('Details stored successfully in database', icon="✅")              

#Menu - Modify or Delete Page                
elif selected == 'Modify or Delete':
    st.markdown("#### View or Update or Delete any data below")
    col1, col2, col3 = st.columns([2,2,4])
    with col1:
        mycursor.execute('select card_holder from business_card_data')
        y = mycursor.fetchall()
        contact = [x[0] for x in y]
        contact.sort()
        selected_contact = st.selectbox('card_holder',contact)
    with col2:
        mode_list = ['','View','Modify','Delete']
        selected_mode = st.selectbox('Mode',mode_list,index = 0)

    #Menu - View Card Data 
    if selected_mode == 'View':
        st.write("")
        st.markdown(f"#### :green[ View {selected_contact}'s Business Card Information below]")
        #st.markdown("#### :green[ View Business Card Information below]")
        col5,col6 = st.columns(2)
        with col5:  
            mycursor.execute(f"select card_holder, designation, company_name, email,mobile_number, website,area,city,state, pin_code from business_card_data where card_holder = '{selected_contact}'")
            y = mycursor.fetchall()
            st.table(pd.Series(y[0],index=['Name', 'Designation', 'company_name', 'Email ID','Mobile Number', 'Website', 'Area', 'city', 'State', 'Pincode'],name='Card Information'))
    
    #Menu - Modify Card Data 
    elif selected_mode == 'Modify':
        st.markdown(f"#### :green[ Update {selected_contact}'s Business Card Information below]")
        mycursor.execute(f"select card_holder, designation, company_name, email,mobile_number, website, area, city,state, pin_code from business_card_data where card_holder = '{selected_contact}'")
        info = mycursor.fetchone()
        col5, col6 = st.columns(2)
        with col5:
            names = st.text_input('Name:', info[0])
            desig = st.text_input('Designation:', info[1])
            Com = st.text_input('Company:', info[2])
            mail = st.text_input('Email ID:', info[3])
            phno1 = st.text_input('Mobile Number:', info[4])
            url = st.text_input('Website:', info[5])
            ar = st.text_input('Area:', info[6])
            cty = st.text_input('City:', info[7])
            stat = st.text_input('State:', info[8])
            pin = int(st.number_input('Pincode:', value=float(info[9])))
            a = st.button("Update it!")
            if a:
                query = f"update business_card_data set card_holder = %s, designation = %s, company_name = %s, email = %s,mobile_number = %s, website = %s,area = %s, city = %s, state = %s, pin_code = %s where card_holder = '{selected_contact}'"
                val = (names, desig, Com, mail,phno1, url,ar, cty,stat, pin)
                mycursor.execute(query, val)
                mydb.commit()
                st.success('Business card information updated successfully', icon="✅")

    #Menu - Delete Card Data 
    elif selected_mode == 'Delete':
        st.markdown(f"#### :green[ Do You Really Want to Delete {selected_contact}'s Business Card Information?]")
        if st.button('Yes, Delete !'):
            query = f"DELETE FROM business_card_data where card_holder = '{selected_contact}'"
            mycursor.execute(query)
            mydb.commit()
            st.success("Business card information deleted from database.", icon="✅")