import streamlit as st
from streamlit_option_menu import option_menu
import os
import json
from PIL import Image
import mysql.connector as sql_db
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests

#Create Dataframes from SQL
#SQL Connection
mydb = sql_db.connect(host="localhost",
                   user="root",
                   password="#Saravanan27",
                   database= "phonepe_data",
                   auth_plugin='mysql_native_password'
                  )
mycursor = mydb.cursor(buffered=True)

#Aggregated Transaction
mycursor.execute("select * from aggr_Transaction;")
mydb.commit()
table1 = mycursor.fetchall()

Aggre_transaction = pd.DataFrame(table1,columns = ("State", "Year", "Quarter", "Transaction_Type", "Transaction_Count", "Transaction_Amount"))

#Aggregated User
mycursor.execute("select * from aggr_user;")
mydb.commit()
table2 = mycursor.fetchall()

Aggre_user = pd.DataFrame(table2,columns = ("States", "Year", "Quarter", "Brands", "Transaction_Count", "Percentage"))

#Aggregated Insurance
mycursor.execute("select * from aggr_insurance;")
mydb.commit()
table7 = mycursor.fetchall()

Aggre_Insurance = pd.DataFrame(table7,columns = ("State", "Year", "Quarter", "Transaction_Type", "Transaction_Count", "Transaction_Amount"))

#Map transaction
mycursor.execute("select * from map_transaction;")
mydb.commit()
table3 = mycursor.fetchall()

Map_transaction = pd.DataFrame(table3,columns = ("State", "Year", "Quarter", "District", "Transaction_Count", "Transaction_Amount"))

#Map Insurance
mycursor.execute("select * from map_insurance;")
mydb.commit()
table8 = mycursor.fetchall()

map_Insurance = pd.DataFrame(table8,columns = ("State", "Year", "Quarter", "District", "Transaction_Count", "Transaction_Amount"))

#Map User
mycursor.execute("select * from map_user;")
mydb.commit()
table4 = mycursor.fetchall()

Map_user = pd.DataFrame(table4,columns = ("State", "Year", "Quarter", "District", "RegisteredUser", "AppOpens"))

#Top Transaction
mycursor.execute("select * from top_transaction;")
mydb.commit()
table5 = mycursor.fetchall()

Top_transaction = pd.DataFrame(table5,columns = ("State", "Year", "Quarter", "PinCode", "Transaction_Count", "Transaction_Amount"))

#Top Insurance
mycursor.execute("select * from top_insurance;")
mydb.commit()
table9 = mycursor.fetchall()

Top_Insurance = pd.DataFrame(table9,columns = ("State", "Year", "Quarter", "Pincode", "Transaction_Count", "Transaction_Amount"))

#Top User
mycursor.execute("select * from top_user;")
mydb.commit()
table6 = mycursor.fetchall()

Top_user = pd.DataFrame(table6, columns = ("State", "Year", "Quarter", "Pincode", "RegisteredUser"))

#Streamlit part
#Setting up Streamlit Page 
icon = Image.open("Logo.png")
st.set_page_config(page_title= "PhonePe Pulse Data Visualization and Exploration",
                   page_icon= icon,
                   layout="wide",
                   initial_sidebar_state="expanded",
                   menu_items={'About': """# This is Data Visualization of PhonePe Pulse Cloned from GitHub Repo"""})

st.sidebar.header(":wave :black[**Welcome to the DashBoard**]")

st.title("PHONEPE DATA VISUALIZATION AND EXPLORATION")
st.write("")

with st.sidebar:
    selected= option_menu("Menu",["Home","About","Explore Data","Top Charts"],
                          icons=["house","graph-up-arrow","bar-chart-line", "exclamation-circle"],
                          menu_icon= "menu-button-wide",
                          default_index=0,
                          styles = {"nav-link": {"font-size":"10px","text-align":"left", "--hover-color": "#6F36AD"},
                                                 "nav-link-selected": {"background-color": "#6F36AD"}})
    
#Menu - Home    
if selected == "Home":

    st.image("PhonePeLogo.jpg")
    st.markdown("## :violet[A User-Friendly Tool Using Streamlit and Plotly]")
    st.write(" ")
    st.write(" ")
    st.markdown("### :violet[Domain :] Fintech")
    st.markdown("### :violet[Technologies used :] Github Cloning, Python, Pandas, MySQL, mysql-connector-python, Streamlit, and Plotly.")
    st.markdown("### :violet[Overview :] In this streamlit web app you can visualize the phonepe pulse data and gain lot of insights on transactions, number of users, top 10 state, district, pincode and which brand has most number of users and so on. Bar charts, Pie charts and Geo map visualization are used to get some insights.")

#Menu - About
if selected == "About":

    st.markdown("## :violet[PhonePe]")
    st.subheader("PhonePe  is an Indian digital payments and financial technology company")
    st.markdown("A leading digital payments platform that enables users to make instant and secure transactions using their mobile phone.")
    st.write("### :violet[****FEATURES****]")
    st.write("****Credit & Debit card linking****")
    st.write("****Bank Balance check****")
    st.write("****Money Storage****")
    st.write("****PIN Authorization****")
    st.write("****No Wallet Top-Up Required****")
    st.write("****Pay Directly From Any Bank To Any Bank A/C****")
    st.write("****Instantly & Free****")
    st.download_button("DOWNLOAD THE APP NOW", "https://www.phonepe.com/app-download/")

#Explore Data == Function Calls
def Transition_Amount_Count_Year(df,year):
    trans_amt_count_year = df[df['Year'] == year]
    trans_amt_count_year.reset_index(drop= True,inplace= True)
    
    trans_amt_count_year_groupBy =trans_amt_count_year.groupby("State")[["Transaction_Count","Transaction_Amount"]].sum()
    trans_amt_count_year_groupBy.reset_index(inplace= True)

    col1,col2 = st.columns(2)

    with col1:

        fig_Ins_Amt = px.bar(trans_amt_count_year_groupBy,x="State",y="Transaction_Amount",title= f"{year} TRANSACTION AMOUNT",width=600,height=650,color_discrete_sequence=px.colors.sequential.Aggrnyl)
        st.plotly_chart(fig_Ins_Amt)

    with col2:
        fig_Ins_Count = px.bar(trans_amt_count_year_groupBy,x="State",y="Transaction_Count",title= f"{year} TRANSACTION COUNT",width=600,height=650,color_discrete_sequence=px.colors.sequential.Bluered_r)
        st.plotly_chart(fig_Ins_Count)

    col1,col2 = st.columns(2)

    with col1:

        url="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
        response = requests.get(url)
        data1 = json.loads(response.content)  
        states_Name_Transaction =[feature["properties"]["ST_NM"] for feature in data1["features"]]
        states_Name_Transaction.sort()

        fig_india_TransAmnt=px.choropleth(trans_amt_count_year_groupBy, geojson= data1, locations= "State", featureidkey= "properties.ST_NM",
                              color= "Transaction_Amount", color_continuous_scale= "Sunsetdark",
                              range_color= (trans_amt_count_year_groupBy["Transaction_Amount"].min(),trans_amt_count_year_groupBy["Transaction_Amount"].max()),
                              hover_name= "State",title = f"{year} TRANSACTION AMOUNT",
                              fitbounds= "locations",width =600, height= 600)
        fig_india_TransAmnt.update_geos(visible =False)                          
        st.plotly_chart(fig_india_TransAmnt)

    with col2:

        fig_india_TransCount=px.choropleth(trans_amt_count_year_groupBy, geojson= data1, locations= "State", featureidkey= "properties.ST_NM",
                                color= "Transaction_Count", color_continuous_scale= "Sunsetdark",
                                range_color= (trans_amt_count_year_groupBy["Transaction_Count"].min(),trans_amt_count_year_groupBy["Transaction_Count"].max()),
                                hover_name= "State",title = f"{year} TRANSACTION COUNT",
                                fitbounds= "locations",width =600, height= 600)
        fig_india_TransCount.update_geos(visible =False)                          
        st.plotly_chart(fig_india_TransCount)

    return trans_amt_count_year     

def Transaction_Amount_Count_Quarter(df,quarter):
    trans_amt_count_Qtr = df[df['Quarter'] == quarter]
    trans_amt_count_Qtr.reset_index(drop= True,inplace= True)

    trans_amt_count_Qtr_groupBy = trans_amt_count_Qtr.groupby("State")[["Transaction_Count","Transaction_Amount"]].sum()
    trans_amt_count_Qtr_groupBy.reset_index(inplace= True)

    col1,col2 = st.columns(2)

    with col1:

        fig_Ins_Amt = px.bar(trans_amt_count_Qtr_groupBy,x="State",y="Transaction_Amount",title= f"{trans_amt_count_Qtr['Year'].min()} Year {quarter} QUARTER TRANSACTION AMOUNT",width=600,height=650,color_discrete_sequence=px.colors.sequential.Burg_r)
        st.plotly_chart(fig_Ins_Amt)

    with col2:    

        fig_Ins_Count = px.bar(trans_amt_count_Qtr_groupBy,x="State",y="Transaction_Count",title= f"{trans_amt_count_Qtr['Year'].min()} Year {quarter} QUARTER TRANSACTION COUNT",width=600,height=650,color_discrete_sequence=px.colors.sequential.Cividis_r)
        st.plotly_chart(fig_Ins_Count)

    col1,col2 = st.columns(2)

    with col1:    

        url="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
        response = requests.get(url)
        data1 = json.loads(response.content)
        st_nms =[feature["properties"]["ST_NM"] for feature in data1["features"]]
        st_nms.sort()

        fig_india_AmtQuarter=px.choropleth(trans_amt_count_Qtr_groupBy, geojson= data1, locations= "State", featureidkey= "properties.ST_NM",
                                color= "Transaction_Amount", color_continuous_scale= "Rainbow",
                                range_color= (trans_amt_count_Qtr_groupBy["Transaction_Amount"].min(),trans_amt_count_Qtr_groupBy["Transaction_Amount"].max()),
                                hover_name= "State",title = f"{trans_amt_count_Qtr['Year'].min()} Year {quarter} QUARTER TRANSACTION AMOUNT",
                                fitbounds= "locations",width =450, height= 600)
        fig_india_AmtQuarter.update_geos(visible =False)                          
        st.plotly_chart(fig_india_AmtQuarter)  

    with col2:    

        fig_india_CountQuarter=px.choropleth(trans_amt_count_Qtr_groupBy, geojson= data1, locations= "State", featureidkey= "properties.ST_NM",
                                color= "Transaction_Count", color_continuous_scale= "Rainbow",
                                range_color= (trans_amt_count_Qtr_groupBy["Transaction_Count"].min(),trans_amt_count_Qtr_groupBy["Transaction_Count"].max()),
                                hover_name= "State",title = f"{trans_amt_count_Qtr['Year'].min()} Year {quarter} QUARTER TRANSACTION COUNT",
                                fitbounds= "locations",width =450, height= 600)
        fig_india_CountQuarter.update_geos(visible =False) 
        st.plotly_chart(fig_india_CountQuarter)

    return trans_amt_count_Qtr       

def Aggregated_Transaction_Type(df,state):
    aggr_States_List = df[df["State"] == state]
    aggr_States_List.reset_index(drop = True,inplace = True)

    Aggr_Trans_Type_GrpBy=aggr_States_List.groupby("Transaction_Type")[["Transaction_Count","Transaction_Amount"]].sum()
    Aggr_Trans_Type_GrpBy.reset_index(inplace = True)

    col1,col2= st.columns(2)
    with col1:

        fig_Aggr_Trans_States_TC=px.pie(data_frame=Aggr_Trans_Type_GrpBy,names="Transaction_Type",values="Transaction_Amount",hole=0.5,color_discrete_sequence=px.colors.sequential.Aggrnyl,width = 500,title= f"{state.upper()} TRANSACTION AMOUNT")
        st.plotly_chart(fig_Aggr_Trans_States_TC)

    with col2:

        fig_Aggr_Trans_States_TC=px.pie(data_frame=Aggr_Trans_Type_GrpBy,names="Transaction_Type",values="Transaction_Count",hole=0.5,color_discrete_sequence=px.colors.sequential.Aggrnyl,width = 500,title= f"{state.upper()} TRANSACTION COUNT")
        st.plotly_chart(fig_Aggr_Trans_States_TC)    

def Aggr_User_Year_Plot(df,year):
    aggr_user_year=df[df["Year"] == year]
    aggr_user_year.reset_index(drop=True,inplace=True)

    aggr_user_year_brand_grpBY=pd.DataFrame(aggr_user_year.groupby("Brands")["Transaction_Count"].sum())
    aggr_user_year_brand_grpBY.reset_index(inplace = True)

    fig_aggr_user_brands=px.bar(aggr_user_year_brand_grpBY, x="Brands", y= "Transaction_Count", title=f"{year} BRANDS AND TRANSACTION COUNT",
                                width=1000,color_discrete_sequence=px.colors.sequential.Aggrnyl,hover_name = "Brands")
    st.plotly_chart(fig_aggr_user_brands)

    return aggr_user_year     

def Aggr_User_Qtr_Plot(df,quarter):
    aggr_user_Qtr_list=df[df["Quarter"] == quarter]
    aggr_user_Qtr_list.reset_index(drop=True,inplace=True)

    aggr_user_year_Qtr_grpBY=pd.DataFrame(aggr_user_Qtr_list.groupby("Brands")["Transaction_Count"].sum())
    aggr_user_year_Qtr_grpBY.reset_index(inplace = True)

    fig_aggr_Qtr_brands=px.bar(aggr_user_year_Qtr_grpBY, x="Brands", y= "Transaction_Count", title=f"{quarter} QUARTER BRANDS AND TRANSACTION COUNT",
                               width=1000,color_discrete_sequence= px.colors.sequential.Magenta_r,hover_name = "Brands")
    st.plotly_chart(fig_aggr_Qtr_brands)
    
    return aggr_user_Qtr_list

def Aggr_User_State_Plot(df,state):
    aggr_user_State_list=df[df["States"] == state]
    aggr_user_State_list.reset_index(drop=True,inplace=True)

    fig_aggr_State_brands= px.line(aggr_user_State_list, x= "Brands", y= "Transaction_Count",hover_data = "Percentage", title=f"{state.upper()} - STATE WISE BRANDS, TRANSACTION COUNT, PERCENTAGE", markers= True,width=1000)
    st.plotly_chart(fig_aggr_State_brands)

def map_insurance_plot_state(df,state):
    map_Ins_State_List=df[df['State'] == state]
    map_Ins_State_List.reset_index(drop = True, inplace = True)

    map_Ins_State_List_gpby=map_Ins_State_List.groupby("District")[["Transaction_Count","Transaction_Amount"]].sum()
    map_Ins_State_List_gpby.reset_index(inplace=True)

    col1,col2=st.columns(2)
    with col1:
        
        fig_map_ins_state_bar=px.bar(map_Ins_State_List_gpby, x= "Transaction_Amount", y="District",orientation = "h",height = 550,
                                     width=600,title=f"{state.upper()} DISTRICTS AND TRANSACTION AMOUNT", color_discrete_sequence= px.colors.sequential.Mint_r)
        st.plotly_chart(fig_map_ins_state_bar)

    with col2:

        fig_map_ins_state_bar=px.bar(data_frame=map_Ins_State_List_gpby, x= "Transaction_Count", y="District",orientation = "h",height = 550,
                                     width=600,title=f"{state.upper()} DISTRICTS AND TRANSACTION COUNT", color_discrete_sequence= px.colors.sequential.Aggrnyl_r)
        st.plotly_chart(fig_map_ins_state_bar)

def map_User_Year(df,year):
    map_user_yr=df[df["Year"] == year]
    map_user_yr.reset_index(drop=True,inplace=True)

    map_user_yr_gb=map_user_yr.groupby("State")[["RegisteredUser","AppOpens"]].sum()
    map_user_yr_gb.reset_index(inplace=True)

    fig_map_user_plot_1= px.line(map_user_yr_gb, x= "State", y= ["RegisteredUser","AppOpens"], markers= True,orientation="v",labels={'State': "State"},
                                 width=1000,height=600,title=f" {year} REGISTERED USERS AND APP OPENS", color_discrete_sequence= px.colors.sequential.Viridis_r)

    st.plotly_chart(fig_map_user_plot_1)

    return map_user_yr

def map_User_Quarter(df,quarter):
    map_user_qtr = df[df["Quarter"] == quarter]
    map_user_qtr.reset_index(drop=True,inplace=True)
    map_user_qtr_gb=map_user_qtr.groupby("State")[["RegisteredUser","AppOpens"]].sum()
    map_user_qtr_gb.reset_index(inplace=True)

    fig_map_user_plot_2= px.line(map_user_qtr_gb, x= "State", y= ["RegisteredUser","AppOpens"], markers= True,
                                    title= f"{df['Year'].min()}, {quarter} QUARTER REGISTERED USER AND APPOPENS",
                                    width= 1000,height=800,color_discrete_sequence= px.colors.sequential.Rainbow_r)
    st.plotly_chart(fig_map_user_plot_2)

    return map_user_qtr

def map_User_State(df,state):
    map_user_state = df[df["State"] == state]
    map_user_state.reset_index(drop=True,inplace=True)
    map_user_state_gb=map_user_state.groupby("District")[["RegisteredUser","AppOpens"]].sum()
    map_user_state_gb.reset_index(inplace=True)

    col1,col2 = st.columns(2)
    with col1:
        fig_map_user_state1=px.bar(map_user_state_gb,x="RegisteredUser",y="District",orientation="h",
            title=f"{state.upper()} REGISTERED USER",height=600,width = 600,
            color_discrete_sequence=px.colors.sequential.Plasma_r)
        st.plotly_chart(fig_map_user_state1)
        
    with col2:
        fig_map_user_state2=px.bar(map_user_state_gb,x="AppOpens",y="District",orientation="h",
                                title=f"{state.upper()} APP OPENS",height=600,width = 600,
                                color_discrete_sequence=px.colors.sequential.Oranges_r)  
        st.plotly_chart(fig_map_user_state2)

def top_user_yr(df,year):
    top_user_year=df[df['Year'] == year]
    top_user_year.reset_index(drop= True, inplace= True)
    top_user_year_gby=pd.DataFrame(top_user_year.groupby(["State","Quarter"])['RegisteredUser'].sum())
    top_user_year_gby.reset_index(inplace= True)
    fig_top_user_yr_plot= px.bar(top_user_year_gby, x= "State", y= "RegisteredUser", barmode= "group", color= "Quarter",
                                width=1000, height= 800, color_continuous_scale= px.colors.sequential.Burgyl,title=f"{year} STATE, QUARTER AND REGISTERED USERS")
    st.plotly_chart(fig_top_user_yr_plot)

    return top_user_year  

def top_user_state(df,state):
    top_user_state=df[df['State'] == state ]
    top_user_state.reset_index(drop= True, inplace= True)
    top_user_state_gby=pd.DataFrame(top_user_state.groupby("Quarter")['RegisteredUser'].sum())
    top_user_state_gby.reset_index(inplace= True)
    fig_top_user_state_plot= px.bar(top_user_state_gby, x= "Quarter", y= "RegisteredUser", barmode= "group",
                                width=1000, height= 800, color_continuous_scale= px.colors.sequential.Magenta,title=f"{state} QUARTER AND REGISTERED USERS")
    st.plotly_chart(fig_top_user_state_plot)

#Questions for Data Analysis
def ques1():
    brand= Aggre_user[["Brands","Transaction_Count"]]
    brand1= brand.groupby("Brands")["Transaction_Count"].sum().sort_values(ascending=False)
    brand2= pd.DataFrame(brand1).reset_index()

    fig_brands= px.pie(brand2, values= "Transaction_Count", names= "Brands", color_discrete_sequence=px.colors.sequential.dense_r,
                       title= "Top Mobile Brands of Transaction_count")
    return st.plotly_chart(fig_brands)

def ques2():
    lt= Aggre_transaction[["State", "Transaction_Amount"]]
    lt1= lt.groupby("State")["Transaction_Amount"].sum().sort_values(ascending= True)
    lt2= pd.DataFrame(lt1).reset_index().head(10)

    fig_lts= px.bar(lt2, x= "State", y= "Transaction_Amount",title= "Top 10 Lowest Transaction Amount and States",
                    color_discrete_sequence= px.colors.sequential.Oranges_r)
    return st.plotly_chart(fig_lts)    

def ques3():
    htd= Map_transaction[["District", "Transaction_Amount","State"]]
    htd1= htd.groupby(["District","State"])["Transaction_Amount"].sum().sort_values(ascending=False)
    htd2= pd.DataFrame(htd1).head(10).reset_index()

    fig_htd= px.pie(htd2, values= "Transaction_Amount", names= "District", title="Top 10 Districts Of Highest Transaction Amount",
                    color_discrete_sequence=px.colors.sequential.Emrld_r,hover_name="State")
    return st.plotly_chart(fig_htd)

def ques4():
    htd= Map_transaction[["District", "Transaction_Amount","State"]]
    htd1= htd.groupby(["District","State"])["Transaction_Amount"].sum().sort_values(ascending=True)
    htd2= pd.DataFrame(htd1).head(10).reset_index()

    fig_htd= px.pie(htd2, values= "Transaction_Amount", names= "District", title="Top 10 Districts of Lowest Transaction Amount",
                    color_discrete_sequence=px.colors.sequential.Greens_r,hover_name="State")
    return st.plotly_chart(fig_htd) 

def ques5():
    sa= Map_user[["State", "AppOpens"]]
    sa1= sa.groupby("State")["AppOpens"].sum().sort_values(ascending=False)
    sa2= pd.DataFrame(sa1).reset_index().head(10)

    fig_sa= px.bar(sa2, x= "State", y= "AppOpens", title="Top 10 Highest States With AppOpens",
                color_discrete_sequence= px.colors.sequential.deep_r)
    return st.plotly_chart(fig_sa)  

def ques6():
    sa= Map_user[["State", "AppOpens"]]
    sa1= sa.groupby("State")["AppOpens"].sum().sort_values(ascending=True)
    sa2= pd.DataFrame(sa1).reset_index().head(10)

    fig_sa= px.bar(sa2, x= "State", y= "AppOpens", title="Top 10 Lowest States With AppOpens",
                color_discrete_sequence= px.colors.sequential.dense_r)
    return st.plotly_chart(fig_sa) 

def ques7():
    stc= Aggre_transaction[["State", "Transaction_Count"]]
    stc1= stc.groupby("State")["Transaction_Count"].sum().sort_values(ascending=True)
    stc2= pd.DataFrame(stc1).head(10).reset_index()

    fig_stc= px.bar(stc2, x= "State", y= "Transaction_Count",title= "Top 10 States with Lowest Transaction Count",
                    color_discrete_sequence= px.colors.sequential.Jet_r)
    return st.plotly_chart(fig_stc)  

def ques8():
    stc= Aggre_transaction[["State", "Transaction_Count"]]
    stc1= stc.groupby("State")["Transaction_Count"].sum().sort_values(ascending=False)
    stc2= pd.DataFrame(stc1).reset_index()

    fig_stc= px.bar(stc2, x= "State", y= "Transaction_Count", title= "States With Highest Transaction Count",
                    color_discrete_sequence= px.colors.sequential.Magenta_r)
    return st.plotly_chart(fig_stc)  

def ques9():
    ht= Aggre_transaction[["State", "Transaction_Amount"]]
    ht1= ht.groupby("State")["Transaction_Amount"].sum().sort_values(ascending= False)
    ht2= pd.DataFrame(ht1).reset_index().head(10)

    fig_lts= px.bar(ht2, x= "State", y= "Transaction_Amount",title= "Highest 10 States With Transaction Amount",
                    color_discrete_sequence= px.colors.sequential.Oranges_r)
    return st.plotly_chart(fig_lts)  

def ques10():
    dt= Map_transaction[["District", "Transaction_Amount","State"]]
    dt1= dt.groupby(["District","State"])["Transaction_Amount"].sum().sort_values(ascending=True)
    dt2= pd.DataFrame(dt1).reset_index().head(50)

    fig_dt= px.bar(dt2, x= "District", y= "Transaction_Amount", title= "Top 50 Districts With Lowest Transaction Amount",
                color_discrete_sequence= px.colors.sequential.Mint_r,hover_name="State")
    return st.plotly_chart(fig_dt)   



#Menu - Explore Data
if selected == "Explore Data":
    
    tab1, tab2, tab3= st.tabs(["Aggregated Analysis", "Map Analysis", "Top Analysis"])

    with tab1 :
        method = st.radio("**Select the Analysis Method**",["Aggregated Insurance Analysis","Aggregated Transaction Analysis","Aggregated User Analysis"])

        if method == "Aggregated Insurance Analysis":
            col1,col2 = st.columns(2)

            with col1:
                years = st.slider("Select the year",Aggre_Insurance['Year'].min(),Aggre_Insurance['Year'].max(),Aggre_Insurance['Year'].min())
            trans_amt_count_year=Transition_Amount_Count_Year(Aggre_Insurance,years)

            col1,col2 = st.columns(2)

            with col1:
                quarters = st.slider("Select the year",trans_amt_count_year['Quarter'].min(),trans_amt_count_year['Quarter'].max(),trans_amt_count_year['Quarter'].min())
            Transaction_Amount_Count_Quarter(trans_amt_count_year,quarters)

        elif method == "Aggregated Transaction Analysis":
            col1,col2 = st.columns(2)

            with col1:
                years_at = st.slider("## :black[Slide to Select any Year]",Aggre_transaction['Year'].min(),Aggre_transaction['Year'].max(),Aggre_transaction['Year'].min())
            aggrg_Transaction_year=Transition_Amount_Count_Year(Aggre_transaction,years_at)

            col1,col2 = st.columns(2)
            with col1:
                state_Year=st.selectbox("## :black[Select any State to explore more]",aggrg_Transaction_year["State"].unique())
            Aggregated_Transaction_Type(aggrg_Transaction_year,state_Year)    

            col1,col2= st.columns(2)
            with col1:
                quarters_at= st.slider("## :black[Slide to Select any Quarter]", aggrg_Transaction_year["Quarter"].min(), aggrg_Transaction_year["Quarter"].max(),aggrg_Transaction_year["Quarter"].min())
            aggrg_Transaction_year_quarter= Transaction_Amount_Count_Quarter(aggrg_Transaction_year, quarters_at)

            col1,col2 = st.columns(2)
            with col1:
            #Select the State for Analyse the Transaction type
                state_Year_Quarter= st.selectbox("## :black[Select any State to explore]",aggrg_Transaction_year_quarter["State"].unique())
            Aggregated_Transaction_Type(aggrg_Transaction_year_quarter,state_Year_Quarter)

        elif method == "Aggregated User Analysis":
            col1,col2= st.columns(2)
            with col1:
                aggr_UYrs= st.selectbox("## :black[Select any Year to explore]",Aggre_user["Year"].unique())
            aguyp=Aggr_User_Year_Plot(Aggre_user,aggr_UYrs)  

            col1,col2= st.columns(2)
            with col1:  
                aggr_UQtrs= st.selectbox("## :black[Select any Quarter to explore]",aguyp["Quarter"].unique())
            aguyq=Aggr_User_Qtr_Plot(aguyp,aggr_UQtrs)   

            col1,col2= st.columns(2)
            with col1: 
                aggr_UStates = st.selectbox("## :black[Select any State to explore]",aguyq["States"].unique()) 
            Aggr_User_State_Plot(aguyq,aggr_UStates)    

    with tab2:
        method = st.radio("**Select the Analysis Method**",["Map Insurance Analysis","Map Transaction Analysis","Map User Analysis"])

        if method == "Map Insurance Analysis":
            col1,col2= st.columns(2)
            with col1:
                map_UYrs= st.slider("## :black[Slide to select any Year to explore]",map_Insurance["Year"].min(),map_Insurance["Year"].max(),map_Insurance["Year"].min())
            state_map_Ins_df=Transition_Amount_Count_Year(map_Insurance,map_UYrs)

            col1,col2= st.columns(2)
            with col1:
                state_map_Ins= st.selectbox("## :black[Select any State to explore more chart]", state_map_Ins_df["State"].unique())
            map_insurance_plot_state(state_map_Ins_df,state_map_Ins)  

            col1,col2= st.columns(2)
            with col1:
                map_UQtrs= st.slider("## :black[Slide to select any Quarter to explore]", state_map_Ins_df["Quarter"].min(), state_map_Ins_df["Quarter"].max(),state_map_Ins_df["Quarter"].min())
            state_map_Ins_QTR_df= Transaction_Amount_Count_Quarter(state_map_Ins_df, map_UQtrs)

            col1,col2= st.columns(2)
            with col1:
                state_map_Ins= st.selectbox("## :black[Select any State to explore more ]", state_map_Ins_QTR_df["State"].unique())            
            map_insurance_plot_state(state_map_Ins_QTR_df, state_map_Ins)

        elif method == "Map Transaction Analysis":
            col1,col2= st.columns(2)
            with col1:
                map_UYrs= st.slider("## :black[Slide to select any Year to explore]",Map_transaction["Year"].min(),Map_transaction["Year"].max(),Map_transaction["Year"].min())
            state_map_Trans_df=Transition_Amount_Count_Year(Map_transaction,map_UYrs)

            col1,col2= st.columns(2)
            with col1:
                state_map_Trans= st.selectbox("## :black[Select any State to explore more]", state_map_Trans_df["State"].unique())
            map_insurance_plot_state(state_map_Trans_df,state_map_Trans)  

            col1,col2= st.columns(2)
            with col1:
                map_UQtrs= st.slider("## :black[Slide to select any Quarter to explore]", state_map_Trans_df["Quarter"].min(), state_map_Trans_df["Quarter"].max(),state_map_Trans_df["Quarter"].min())
            state_map_Trans_QTR_df= Transaction_Amount_Count_Quarter(state_map_Trans_df, map_UQtrs)

            col1,col2= st.columns(2)
            with col1:
                state_map_Trans= st.selectbox("## :black[Select any State to explore more ]", state_map_Trans_QTR_df["State"].unique())            
            map_insurance_plot_state(state_map_Trans_QTR_df, state_map_Trans)

        elif method == "Map User Analysis":

            col1,col2= st.columns(2)
            with col1:
                year_map_User= st.selectbox("## :black[Select any Year to explore]", Map_user["Year"].unique())            
            map_user_by_year = map_User_Year(Map_user, year_map_User)

            col1,col2= st.columns(2)
            with col1:
                quarter_map_User= st.selectbox("## :black[Select any Quarter to explore ]",map_user_by_year["Quarter"].unique())
            map_user_by_Qtr= map_User_Quarter(map_user_by_year,quarter_map_User)

            col1,col2= st.columns(2)
            with col1:
                state_map_User= st.selectbox("## :black[Select any State to explore more sights]",map_user_by_Qtr["State"].unique())
            map_User_State(map_user_by_Qtr, state_map_User)

    with tab3:
        method = st.radio("**Select the Analysis Method**",["Top Insurance Analysis", "Top Transaction Analysis", "Top User Analysis"])

        if method == "Top Insurance Analysis":
            col1,col2= st.columns(2)
            with col1:
                top_Ins_Yrs= st.slider("## :black[Slide to select any Year to explore more plots]",Top_Insurance["Year"].min(),Top_Insurance["Year"].max(),Top_Insurance["Year"].min())
            state_top_Ins_df=Transition_Amount_Count_Year(Top_Insurance,top_Ins_Yrs)

            col1,col2= st.columns(2)
            with col1:
                top_Ins_Qtr= st.slider("## :black[Slide to select any Quarter to explore more plots]", state_top_Ins_df["Quarter"].min(), state_top_Ins_df["Quarter"].max(),state_top_Ins_df["Quarter"].min())
            state_top_ins_qtr= Transaction_Amount_Count_Quarter(state_top_Ins_df, top_Ins_Qtr)

        elif method == "Top Transaction Analysis":
            col1,col2= st.columns(2)
            with col1:
                top_Trans_Yrs= st.slider("## :black[Slide to select any Year to explore more plots]",Top_transaction["Year"].min(),Top_transaction["Year"].max(),Top_transaction["Year"].min())
            state_top_Trans_df=Transition_Amount_Count_Year(Top_transaction,top_Trans_Yrs)

            col1,col2= st.columns(2)
            with col1:
                top_Trans_Qtr= st.slider("## :black[Slide to select any Quarter to explore more plotss]", state_top_Trans_df["Quarter"].min(), state_top_Trans_df["Quarter"].max(),state_top_Trans_df["Quarter"].min())
            state_top_trans_qtr= Transaction_Amount_Count_Quarter(state_top_Trans_df, top_Trans_Qtr)

        elif method == "Top User Analysis":
            col1,col2= st.columns(2)
            with col1:
                top_User_Yrs= st.selectbox("## :black[Select any Year to explore charts]",Top_user["Year"].unique())
            top_User_Yrs_df= top_user_yr(Top_user,top_User_Yrs)

            col1,col2= st.columns(2)
            with col1:
                top_User_States= st.selectbox("## :black[Select any State to more explore]", top_User_Yrs_df["State"].unique())
            top_User_Yrs_State_df= top_user_state(top_User_Yrs_df,top_User_States)

#Menu - Top Charts
if selected == "Top Charts":

    ques= st.selectbox("**Select the Question**",('Top Brands Of Mobiles Used','Top 10 Lowest Transaction Amount and States',
                                  'Top 10 Districts Of Highest Transaction Amount','Top 10 Districts of Lowest Transaction Amount',
                                  'Top 10 Highest States With AppOpens','Top 10 Lowest States With AppOpens','Top 10 States with Lowest Transaction Count',
                                 'States With Highest Transaction Count','Highest 10 States With Transaction Amount',
                                 'Top 50 Districts With Lowest Transaction Amount'))
    
    if ques=="Top Brands Of Mobiles Used":
        ques1()

    elif ques=="Top 10 Lowest Transaction Amount and States":
        ques2()

    elif ques=="Top 10 Districts Of Highest Transaction Amount":
        ques3()

    elif ques=="Top 10 Districts of Lowest Transaction Amount":
        ques4()

    elif ques=="Top 10 Highest States With AppOpens":
        ques5()

    elif ques=="Top 10 Lowest States With AppOpens":
        ques6()

    elif ques=="Top 10 States with Lowest Transaction Count":
        ques7()

    elif ques=="States With Highest Transaction Count":
        ques8()

    elif ques=="Highest 10 States With Transaction Amount":
        ques9()

    elif ques=="Top 50 Districts With Lowest Transaction Amount":
        ques10()   