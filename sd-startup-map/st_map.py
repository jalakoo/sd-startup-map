import streamlit as st
from models import Startup
import logging
import pandas as pd

def add_stmap(startups: list[Startup]):
    map_data = pd.DataFrame({
        'latitude': [s.latitude for s in startups],
        'longitude': [s.longitude for s in startups]
    })
    map_data['info'] = [s.name for s in startups]
    st.map(map_data)
