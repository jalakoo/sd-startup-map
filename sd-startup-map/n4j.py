from neo4j import GraphDatabase
import os

host = os.environ.get('NEO4J_HOST')
user = os.enviorn.get('NEO4J_USER')
password = os.environ.get('NEO4J_PASSWORD')

# driver = GraphDatabase.driver(host, auth=(user, password))

# Experimental query
def execute_query(query, params={}):
    # Returns a tuple of records, summary, keys
    with GraphDatabase.driver(host, auth=(user, password)) as driver:
        return driver.execute_query(query, params)