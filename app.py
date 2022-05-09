
from secrets import choice
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns

from ger_db_app import germany 
from wrld_db_app import world
from home_app import home

# page settings
st.set_page_config(page_title= 'Covid-19 Dashboard', 
# set page icon
page_icon="🦠",
# wide page layout to display all I want
layout= 'wide',
# side bar should be collapsed at first
initial_sidebar_state='expanded',
# menu sited
# page theme

#menu_items = 'About' : ,'Get Help': , 'Report a bug':
)

def main():


    


    # sidebar definitions

    st.sidebar.title('Covid19 Dashboard Menu')
    menu = ['Home','Statistics Germany', 'Statistics World', 'About']
    choice = st.sidebar.selectbox('', menu)
   # btn_menu = st.sidebar.button(label='Menu')
    #btn_ger = st.sidebar.button(label='Germany')

    if choice == 'Statistics World':
        world()
        
    elif choice == 'Statistics Germany':
        germany()







   

if __name__ == '__main__':
    main()



