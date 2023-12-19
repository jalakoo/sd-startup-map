import streamlit as st
from streamlit_js_eval import streamlit_js_eval
from n4j import execute_query
from pydantic import TypeAdapter
from models import Startup
import logging
import pandas as pd
from st_map import add_stmap
from folium_map import add_folium_map
from pydeck_map import add_pydeck_map
from search_list import add_search_list
import streamlit.components.v1 as components
import os
from dotenv import load_dotenv


# Page Config
st.set_page_config(
    layout="wide",
    initial_sidebar_state='collapsed'
)
# This doesn't appear to work at all
# css='''
# <style>
#     section.main>div {
#         padding-bottom: 1rem;
#     }
#     [data-testid="column"]>div>div>div>div>div {
#         overflow: auto;
#         height: 70vh;
#     }
# </style>
# '''
# st.markdown(css, unsafe_allow_html=True)

st.title('SD Startup Map')
# screen_width = streamlit_js_eval(js_expressions='window.innerWidth', key = 'SCR')

with st.sidebar:
    load_dotenv()
    openai_env_key = os.getenv("OPENAI_API_KEY")
    if "OPENAI_KEY" not in st.session_state:
        st.session_state["OPENAI_KEY"] = openai_env_key
    openai_key = st.text_input("OpenAI API Key", st.session_state["OPENAI_KEY"], type="password")
    if openai_key != st.session_state["OPENAI_KEY"]:
        st.session_state["OPENAI_KEY"] = openai_key

# Get startup data
records, summary, keys = execute_query("MATCH (n:Company)-[:HAS_OFFICE]->(l:Location) WHERE l.Latitude is not null RETURN n.Name as name, n.Url as url, n.Description as description, l.Address as address, l.City as city, l.State as state, l.ZipCode as zip, l.Latitude as latitude, l.Longitude as longitude")
ta = TypeAdapter(list[Startup])
startups = ta.validate_python(records)

add_pydeck_map(startups)
# add_stmap(startups)
# add_folium_map(startups)