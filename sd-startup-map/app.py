import streamlit as st
import folium
from streamlit_folium import st_folium, folium_static
from streamlit_js_eval import streamlit_js_eval
from n4j import execute_query
from models import Company, Tag
import statistics
from sidebar import sidebar

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

st.title("Experimental SD Startup Map")

sidebar()


@st.cache_data
def get_tags():
    tags_query = """
    MATCH (c:Company)-[:TAGGED]-(t)
    RETURN DISTINCT t
    ORDER BY t.Name
    """
    records, _, _ = execute_query(tags_query, {})
    results = []
    for r in records:
        # print(f"process tag record: {r}")
        data = r.data()["t"]
        try:
            tag = Tag(**data)
            results.append(tag)
        except Exception as e:
            print(f"\nProblem parsing Tag record: {r}: {e}")
            continue
    return results


@st.cache_data
def get_companies(tags: list[str]):

    print(f"\ntags for retrieving companies: {tags}")

    if len(tags) > 0:
        query = """
        MATCH (l:Location)<-[:HAS_OFFICE]-(c:Company)-[:TAGGED]->(t)
        WHERE t.Name IN $tags
        RETURN DISTINCT c.Id as Id, c.Description as Description, c.StartupYear as StartupYear, c.LinkedInUrl as LinkedInUrl, c.Url as Url, c.Name as Name, c.Logo as Logo, l.Latitude as Lat, l.Longitude as Lon
        """
        params = {"tags": tags}
    else:
        query = """
        MATCH (l:Location)<-[:HAS_OFFICE]-(c:Company)-[:TAGGED]->(t)
        RETURN DISTINCT c.Id as Id, c.Description as Description, c.StartupYear as StartupYear, c.LinkedInUrl as LinkedInUrl, c.Url as Url, c.Name as Name, c.Logo as Logo, l.Latitude as Lat, l.Longitude as Lon
        """
        params = {}

    records, _, _ = execute_query(query, params)

    # print(f"Company query response: {records}")

    results = []
    for r in records:
        data = r.data()
        # print(f"company record data: {data}")
        try:
            company = Company(**data)
            results.append(company)
        except Exception as e:
            print(f"\nProblem parsing Company record: {r}: {e}")
            continue

    return results


tags_list = get_tags()
tags = [t.Name for t in tags_list]

# Keyword based searching
keywords = st.multiselect("Keyword Search", tags)

companies = get_companies(keywords)

st.text(f"Found companies: {len(companies)}")

# Auto find median lat and lons
lats = [c.Lat for c in companies if c.Lat is not None]
median_lat = statistics.median(lats)
lons = [c.Lon for c in companies if c.Lon is not None]
median_lon = statistics.median(lons)


# c1, c2 = st.columns([3, 1])
# with c1:
m = folium.Map(location=[median_lat, median_lon], zoom_start=10, control_scale=True)

# Harcoded lat and lons
# San Diego
# default_lat = 32.715736
# default_lon = -117.161087

# m = folium.Map(location=[default_lat, default_lon], zoom_start=9, controll_scale=True)

for c in companies:
    html = ""  # Reset
    if c.Lat is None or c.Lon is None:
        continue
    # Create a popup with the HTML content
    html = f"""
    <h2>{c.Name}</h2>
    <p>{c.Description}</p>
    <a href="{c.Url}" target="_blank">{c.Url}</a>
    """
    # if c.Logo is not None:
    #     html = c.Logo + html
    if c.LinkedInUrl is not None:
        html += f"<br><br><a href='{c.LinkedInUrl}' target='_blank' rel='noopener noreferrer'>{c.LinkedInUrl}</a>"
    iframe = folium.IFrame(html, width=300, height=200)
    popup = folium.Popup(iframe, min_width=300, max_width=300)

    # Add the marker to the map
    folium.Marker([c.Lat, c.Lon], popup=popup, tooltip=c.Name).add_to(m)

# Loop through each row in the dataframe
# for i,row in df.iterrows():
#     #Setup the content of the popup
#     iframe = folium.IFrame('Well Name:' + str(row["Well Name"]))

#     #Initialise the popup using the iframe
#     popup = folium.Popup(iframe, min_width=300, max_width=300)

#     #Add each row to the map
#     folium.Marker(location=[row['latitude'],row['longitude']],
#                   popup = popup, c=row['Well Name']).add_to(m)

# Find current screen width - NOT dynamic. Page needs to be refreshed to adjust to a resized screen
screen_width = streamlit_js_eval(js_expressions="window.innerWidth", key="SCR")

map_data = st_folium(m, width=screen_width)

st.session_state["map_data"] = map_data

# with c2:
#     # TODO:
#     # Display Startup Info

#     # print(f"st_data: {st_data}")
#     # Sample st_data
#     # {'last_clicked': None, 'last_object_clicked': {'lat': 33.1302, 'lng': -117.167}, 'last_object_clicked_tooltip': 'SigParser', 'last_object_clicked_popup': '', 'all_drawings': [], 'last_active_drawing': None, 'bounds': {'_southWest': {'lat': 32.730685662660896, 'lng': -117.89016723632814}, '_northEast': {'lat': 33.535671379525525, 'lng': -116.51000976562501}}, 'zoom': 10, 'last_circle_radius': None, 'last_circle_polygon': None, 'center': {'lat': 33.13410130507293, 'lng': -117.20008850097658}}
#     if st_data["last_object_clicked"] is not None:
#         print(f'last_object_clicked: {st_data["last_object_clicked"]}')
#         # cl = st_data["last_object_clicked_popup"]
#         # st.text(cl.Name)
#     # st.empty()

#     # TODO:
#     # Optionally Display Editing data

#     # TODO:
#     # Display Add New
