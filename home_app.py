from pyparsing import Word
import streamlit as st

from ger_db_app import germany
from wrld_db_app import world


def home():

    # title definitions
    st.title("Covid-19 Dashboard")
    st.text("This dashboard shows an analysis of the global pandemic situation")
    st.text("Maybe an approach to visualize the impact of vaccination on covid numbers can be managed")

    st.text("Which Dashboard would you like to see?")
    
    

    col1, col2 = st.columns(2)


    with col1:
            btn_ger = st.button('Germany', key='btn_ger')
    if btn_ger: germany()
    with col2:
            btn_wrld = st.button('World', key='btn_wrld')
            
    if btn_wrld: world()
        


    # if btn_ger:
    #     germany()
    # elif btn_wrld:
    #     world()
    # else:
    #     home()

    if __name__ == '__home__':
        home()