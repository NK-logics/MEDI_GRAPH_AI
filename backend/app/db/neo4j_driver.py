from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

URI = "neo4j+s://abe97aaf.databases.neo4j.io"
USER = "abe97aaf"
PASSWORD = "hZTfexXMd9EM-27tNai9awKVFVWHDNaVWqGcjCjk_yw"

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

def get_session():
    return driver.session()