import os

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

# Use neo4j+ssc for environments with self-signed cert chains.
URI = os.getenv("NEO4J_URI", "neo4j+ssc://abe97aaf.databases.neo4j.io")
USER = os.getenv("NEO4J_USER", "abe97aaf")
PASSWORD = os.getenv("NEO4J_PASSWORD", "hZTfexXMd9EM-27tNai9awKVFVWHDNaVWqGcjCjk_yw")

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))


def get_session():
    return driver.session()
