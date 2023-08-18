# -*- coding: utf-8 -*-
"""Data Pipelines with Neo4j - Dennis Mutai.ipynb

Automatically generated by Colaboratory.

### **Background Information**

You have been hired by a telecommunications company that wants to optimize their business
processes. They have a Neo4j graph database that contains information about their customers,
their subscriptions, and the services they are using. However, they also want to store this data
in a more traditional relational database to allow for easier querying and analysis. They have
asked you to create a data pipeline that extracts data from their Neo4j database, transforms it
using pandas, and loads it into a Postgres database.

**Guidelines**

    1. Extracting data from Neo4j:

    2. Transforming data using Pandas:

    3. Loading data into Postgres:
"""

!pip install neo4j

# Import required libraries
from neo4j import GraphDatabase
import pandas as pd
import psycopg2

# Define Neo4j connection details
neo4j_uri = "neo4j+s://432d4b02.databases.neo4j.io"
neo4j_user = "neo4j"
neo4j_password = "TyObWimJ38yH2rFw66gVeWwzIW2gUzksWKvQ4b6ZN5s"

driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

# Define Postgres connection details
pg_host = '157.245.102.81'
pg_port = '5432'
pg_database = 'dq'
pg_user = 'postgres'
pg_password = 'E*3b8km$dpmRLLuf1Rs$'

# Define Neo4j query to extract data
neo4j_query = """
MATCH (c:Customer)-[:HAS_SUBSCRIPTION]->(s:Subscription)-[:USES]->(sr:Service)
RETURN c.customer_id, s.subscription_id, sr.service_id, s.start_date, s.end_date, s.price
"""

# Define function to extract data from Neo4j and return a Pandas DataFrame
def extract_data():
    # Connect to Neo4j
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

    # Define a Cypher query to retrieve the data
    query = """
    MATCH (c:Customer)-[s:SUBSCRIBES_TO]->(sv:Service)
    RETURN c.id AS customer_id, s.start_date AS start_date, s.end_date AS end_date, s.price AS price,
          sv.id AS service_id, sv.name AS service_name
    """

    # Execute the query and retrieve the data
    with driver.session() as session:
        results = session.run(query)
        data = [dict(row) for row in results]

    # Convert the data to a pandas DataFrame
    df = pd.DataFrame(data)
    return df

from datetime import datetime
import logging

# Define function to transform data
def transform_data(df):
    # Convert date fields to datetime objects
    # df['start_date'] = df['start_date'].apply(lambda x: datetime.fromisoformat(str(x)))
    # df['end_date'] = df['end_date'].apply(lambda x: datetime.fromisoformat(str(x)) if x else pd.NaT)

    try:
      df["start_date"] = pd.to_datetime(df["start_date"],format='%d-%m-%Y')
      df["end_date"] = pd.to_datetime(df["end_date"],format='%d-%m-%Y')


      # Remove null values
      df = df.dropna(subset=['start_date', 'end_date'], how='any')

      df.dropna(inplace=True)

      # Create a new column for the duration of the service in days
      df['duration_days'] = (df['end_date'] - df['start_date']).dt.days

    except Exception as e:
        err = "Transform() error - "+str(e)
        logging.debug(err)

    return df

# Define function to load data into Postgres
def load_data(df):
    # Connect to Postgres
    conn = psycopg2.connect(host=pg_host, database=pg_database, user=pg_user, password=pg_password)

    # Create table if it doesn't exist
    with conn.cursor() as cursor:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS telecom_data (
            customer_id INTEGER,
            subscription_id INTEGER,
            service_id INTEGER,
            start_date DATE,
            end_date DATE,
            price FLOAT
        )
        """)

    # Insert data into table
    for index, row in df.iterrows():
            cursor.execute('''INSERT INTO telecom_data (customer_id, subscription_id, service_id, start_date, end_date, price)
                              VALUES (%s, %s, %s, %s, %s, %s)''', (row['customer_id'], row['subscription_id'], row['service_id'], row['start_date'], row['end_date'], row['price']))

    conn.commit()
    conn.close()

# Define main function
def main():
    # Extract data from Neo4j
    df = extract_data()

    # Transform data using Pandas
    transformed_df = transform_data(df)

    # Load data into Postgres
    load_data(transformed_df)

# Call main function
if __name__ == "__main__":
    main()
