import streamlit as st
import folium
from streamlit_folium import st_folium, folium_static
from streamlit_js_eval import streamlit_js_eval
from n4j import execute_query
from pydantic import TypeAdapter
from models import Startup
import logging

# Page Config
st.set_page_config(layout="wide")
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

# Get startup data
records, summary, keys = execute_query("MATCH (n:Company)-[:HAS_OFFICE]->(l:Location) WHERE l.Latitude is not null RETURN n.Name as name, n.Url as url, n.Description as description, l.Address as address, l.Latitude as latitude, l.Longitude as longitude")
ta = TypeAdapter(list[Startup])
startups = ta.validate_python(records)


# Find optimum lat and lon
lats = [s.latitude for s in startups]
lons = [s.longitude for s in startups]
avg_lat = sum(lats)/len(lats)
# Adjust for marker icon height
adjusted_lat = avg_lat + (avg_lat * .002)
avg_lon = sum(lons)/len(lons)
default_lat = adjusted_lat
default_lon = avg_lon

c1,c2 = st.columns([7,1])

with c1:
    # Folium map
    m = folium.Map(location=[default_lat, default_lon], zoom_start=10, controll_scale=True)
    # Add records to Folium
    for s in startups:
        html = f"""
            <h1>{s.name}</h1><br>
        {s.description}
        <p>
    <a href="{s.url}">Official Link</a>
        </p>
    """
        folium.Marker(
            location=[s.latitude, s.longitude],
            tooltip=s.name,
            popup=folium.Popup(html) 
        ).add_to(m)

with c2:
    # List view
    st.write(f'Startups: {len(startups)}')
    # for s in startups:
    #     st.write(s.name)
        # st.markdown(f"""
        # *{s.name}*\n
        # {s.description}\n
        # [Official Link]({s.url})
        # """)

def return_on_hover():
    print('hello')



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
# st_data = st_folium(m, width=screen_width)

# Static map for use within a set width
# map = folium_static(m)

# For capturing clicked item
out = st_folium(m, width=screen_width)
st.write(out["last_object_clicked_popup"])