import streamlit as st
import folium
from streamlit_folium import st_folium, folium_static
from streamlit_js_eval import streamlit_js_eval
from n4j import execute_query
from models import Company, Tag
import statistics

st.set_page_config(layout="wide")

st.title("Experimental SD Startup Map")


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


m = folium.Map(location=[median_lat, median_lon], zoom_start=10, control_scale=True)

# Harcoded lat and lons
# San Diego
# default_lat = 32.715736
# default_lon = -117.161087

# m = folium.Map(location=[default_lat, default_lon], zoom_start=9, controll_scale=True)


for c in companies:
    if c.Lat is None or c.Lon is None:
        continue
    folium.Marker([c.Lat, c.Lon], popup=c.Name, tooltip=c.Name).add_to(m)

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

st_data = st_folium(m, width=screen_width)
