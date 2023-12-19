import pydeck as pdk 
import pandas as pd
from datetime import datetime as dt, timedelta 
from datetime import date, time
import re 
import streamlit as st 


def on_click(info):
    print(f'on_click: {info}')
    st.write(info)

def add_pydeck_map(startups):

    RED_PIN = "https://res.cloudinary.com/dqjkf4zsf/image/upload/v1702934467/red_pin_cgdnac.png"
    GREY_PIN = "https://res.cloudinary.com/dqjkf4zsf/image/upload/v1702934467/grey_pin_lcrlr1.png"
    GREEN_PIN = "https://res.cloudinary.com/dqjkf4zsf/image/upload/v1702934466/green_pin_ihruv4.png"


    icon_data = {
        "url": RED_PIN,
        "width": 200,
        "height": 200,
        "anchorY": 200,
    }

    df = pd.DataFrame({
        'name': [s.name for s in startups],
        'address': [s.address for s in startups],
        'description': [s.description for s in startups],
        'url': [s.url for s in startups],
        'lat': [s.latitude for s in startups],
        'lon': [s.longitude for s in startups],
        "icon_data" : [icon_data for s in startups]
    })



    # define the view (if fewer than 10 locations focus on one corner)
    if len(df) >= 10:
        view = pdk.data_utils.compute_view(df[["lon", "lat"]], 0.9)
    else: 
        view = pdk.ViewState(longitude=max(df['lon']),
        latitude=max(df['lat']), zoom=4)


    # build the icon layer 
    icon_layer = pdk.Layer(
        type="IconLayer",
        data=df,
        get_icon="icon_data",
        get_size=4,
        size_scale=8,
        get_position=["lon", "lat"],
        on_click = on_click,
        pickable=True
    )

    # set up the tool tip
    # Configuration info: https://deckgl.readthedocs.io/en/latest/tooltip.html
    tooltip = {
        "html": "<b>{name},</b> <br/> {description}, <br/> {address}, <br/> {url}",
        "style": {
                "backgroundColor": "#FFFFFF",
                "color": "#000000"
        }
    }

    # Event handling info: https://deckgl.readthedocs.io/en/latest/event_handling.html

    # compile the map 
    r = pdk.Deck(layers=[icon_layer], initial_view_state=view, tooltip=tooltip)

    # Pydeck embedded in streamlit can not process event handling
    # r.deck_widget.on_click(on_click)

    # set up the chart 
    st.pydeck_chart(r)