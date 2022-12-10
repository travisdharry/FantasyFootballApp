# Import dependencies
import os
import pandas as pd
import psycopg2
from sqlalchemy import create_engine

# Find environment variables
DATABASE_URL = os.environ.get("DATABASE_URL", None)
# sqlalchemy deprecated urls which begin with "postgres://"; now it needs to start with "postgresql://"
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# query the database, return a dataframe
def read_db(tableName):
    # Ensure there are no pre-existing connections
    connection = False
    try:
        # Connect to database
        engine = create_engine(DATABASE_URL)
        connection = engine.connect()
        # Write query
        query = f'SELECT * FROM {tableName}'
        # Execute query and convert the response to a pandas df
        result = pd.read_sql(query, connection)
        return result
    # If there is an error interacting with the db, raise the error
    except (Exception, psycopg2.Error) as error:
        raise error
    finally:
        # If the connection was opened, close it
        if connection:
            connection.close()

# Write a new table to the database
def write_df(df, tableName, dataDef):
    # Ensure there are no pre-existing connections
    connection = False
    try:
        # Connect to database
        engine = create_engine(DATABASE_URL)
        # Create psycopg2 connection
        connection = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = connection.cursor()
        # Create table if it does not already exist
        query = f'CREATE TABLE IF NOT EXISTS {tableName}({dataDef})'
        cursor.execute(query)
        connection.commit()
        # Populate table with data
        df.to_sql(tableName, engine, if_exists='replace', index = False)
    # If there is an error interacting with the db, raise the error
    except (Exception, psycopg2.Error) as error:
        raise error
    finally:
        # If the connection was opened, close it
        if connection:
            cursor.close()
            connection.close()


# # Write a new table to the database
# def write_df(df, tableName, dataDef):
#     # Ensure there are no pre-existing connections
#     connection = False
#     try:
#         # Connect to database
#         connection = psycopg2.connect(DATABASE_URL, sslmode='require')
#         engine = create_engine(DATABASE_URL)
#         cursor = connection.cursor()
#         # Create table if it does not already exist
#         query = f'CREATE TABLE IF NOT EXISTS {tableName}({dataDef})'
#         cursor.execute(query)
#         connection.commit()
#         # Populate table with data
#         df.to_sql(tableName, engine, if_exists='replace', index = False)
#     # If there is an error interacting with the db, raise the error
#     except (Exception, psycopg2.Error) as error:
#         raise error
#     finally:
#         # If the connection was opened, close it
#         if connection:
#             cursor.close()
#             connection.close()