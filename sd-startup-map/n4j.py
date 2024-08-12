from neo4j import GraphDatabase
import streamlit as st


# Experimental query
def execute_query(query, params={}):

    host = st.secrets["NEO4J_URI"]
    user = st.secrets["NEO4J_USERNAME"]
    password = st.secrets["NEO4J_PASSWORD"]

    # Returns a tuple of records, summary, keys
    with GraphDatabase.driver(host, auth=(user, password)) as driver:
        return driver.execute_query(query, params)
