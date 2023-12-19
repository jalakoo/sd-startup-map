import folium
from map_utils import center_coordinates
from streamlit_folium import st_folium, folium_static
from streamlit_js_eval import streamlit_js_eval
import folium
import streamlit as st

def add_folium_map(startups):
    
    if "LAST_STARTUP_CLICKED" not in st.session_state:
        st.session_state["LAST_STARTUP_CLICKED"] = None

    # Get map center based off of startup coordinates
    lat,lon = center_coordinates(startups)

    # Folium map
    m = folium.Map(location=[lat,lon], zoom_start=10, controll_scale=True)
    
    # Add records to Folium
    for s in startups:
        html = f"""
            <h1>{s.name}</h1><br>
        {s.description}
        <p>
    <a href="{s.url}">Official Link</a>
        </p>
    """
        
        color = "red"
        if st.session_state["LAST_STARTUP_CLICKED"] == s.name:
            color = "green"
        folium.Marker(
            location=[s.latitude, s.longitude],
            tooltip=s.name,
            popup=folium.Popup(html),
            icon=folium.Icon(color=color)
        ).add_to(m)

    # Static map for use within a set width
    # map = folium_static(m)
        
    screen_width = streamlit_js_eval(js_expressions='window.innerWidth', key = 'SCR')
    out = st_folium(m, width=screen_width)

    # Sample out from click event:
    

    # {'last_clicked': None, 'last_object_clicked': {'lat': 33.1302, 'lng': -117.167}, 'last_object_clicked_tooltip': 'SigParser', 'last_object_clicked_popup': 'SigParser\n\nAutomate contact capture for sales and marketing teams.\nOfficial Link\n\n', 'all_drawings': [], 'last_active_drawing': None, 'bounds': {'_southWest': {'lat': 32.87382044499353, 'lng': -117.66975402832033}, '_northEast': {'lat': 33.276583535317876, 'lng': -116.68304443359376}}, 'zoom': 11, 'last_circle_radius': None, 'last_circle_polygon': None, 'center': {'lat': 33.075432481213326, 'lng': -117.17639923095705}}

    last_clicked = out.get('last_object_clicked_tooltip', None)
    if last_clicked is not None and last_clicked!= st.session_state["LAST_STARTUP_CLICKED"]:
        st.session_state["LAST_STARTUP_CLICKED"] = last_clicked
        st.experimental_rerun()
    
    print(f'out: {out}')
