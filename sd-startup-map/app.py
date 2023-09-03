import streamlit as st
import folium
from streamlit_folium import st_folium, folium_static
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(layout="wide")

st.title('Experimental SD Startup Map')

# TODO: Call for all data from neo4j
# TODO: Convert imported data into a dataframe

default_lat = 32.715736
default_lon = -117.161087

m = folium.Map(location=[default_lat, default_lon], zoom_start=10, controll_scale=True)
# m = folium.Map(location=[df.latitude.mean(), df.longitude.mean()], 
#                  zoom_start=3, control_scale=True)

#Loop through each row in the dataframe
# for i,row in df.iterrows():
#     #Setup the content of the popup
#     iframe = folium.IFrame('Well Name:' + str(row["Well Name"]))
    
#     #Initialise the popup using the iframe
#     popup = folium.Popup(iframe, min_width=300, max_width=300)
    
#     #Add each row to the map
#     folium.Marker(location=[row['latitude'],row['longitude']],
#                   popup = popup, c=row['Well Name']).add_to(m)

# Find current screen width - NOT dynamic. Page needs to be refreshed to adjust to a resized screen
screen_width = streamlit_js_eval(js_expressions='window.innerWidth', key = 'SCR')

st_data = st_folium(m, width=screen_width)