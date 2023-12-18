from neo4j import GraphDatabase
import os

host = os.environ.get('NEO4J_URI')
user = os.environ.get('NEO4J_USERNAME')
password = os.environ.get('NEO4J_PASSWORD')

# Experimental query
def execute_query(query, params={}):
    # Returns a tuple of records, summary, keys
    with GraphDatabase.driver(host, auth=(user, password)) as driver:
        return driver.execute_query(query, params)