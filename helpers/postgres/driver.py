import psycopg2
import pandas as pd
import logging
import os

DATABASE_URL = os.getenv("DATABASE_URL")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PostgresDriver:
    @classmethod
    def connect_to_db(cls):
        """Connect to the PostgreSQL database"""
        try:
            connection = psycopg2.connect(DATABASE_URL)
            connection.autocommit = True  # Ensures changes are committed automatically

            # must run
            # kubectl port-forward svc/postgres 5432:5432

            # connection = psycopg2.connect(
            #     host="localhost",
            #     port=5432,
            #     dbname="staging_db",
            #     user="admin_user",
            #     password="admin_password"
            # )
            logger.info("✅ Connection to the database successful")
            return connection
        except Exception as e:
            logger.error(f"❌ Failed to connect to the database: {e}")
            raise

    @classmethod
    def get_query(cls, query: str):
        """Fetch data from the database and return as a Pandas DataFrame"""
        connection = None
        try:
            connection = cls.connect_to_db()
            df = pd.read_sql(query, connection)

            if not df.empty:
                logger.info(f"✅ Query executed successfully. Rows fetched: {len(df)}")
                logger.debug(df.head(5))  # Logs first 5 rows (optional)
            else:
                logger.info("⚠️ Query returned no results.")

            return df
        except Exception as e:
            logger.error(f"❌ Error executing query: {e}")
            return None
        finally:
            if connection:
                connection.close()
                logger.info("🔌 Connection closed.")

    @classmethod
    def put_query(cls, query: str, values=None):
        """Execute an insert/update/delete query"""
        connection = None
        try:
            connection = cls.connect_to_db()
            with connection.cursor() as cursor:
                if values:
                    cursor.execute(query, values)  # Using parameterized query
                else:
                    cursor.execute(query)
                logger.info(f"✅ Query executed successfully: {query}")
        except Exception as e:
            logger.error(f"❌ Error executing query: {e}")
            return None
        finally:
            if connection:
                connection.close()
                logger.info("🔌 Connection closed.")

    @classmethod
    def create_table(cls, table_name: str, columns: dict):
        """Create a table in the PostgreSQL database"""
        connection = None
        try:
            connection = cls.connect_to_db()
            cursor = connection.cursor()

            # Check if the table already exists
            cursor.execute(
                f"""
                SELECT EXISTS (
                    SELECT 1 
                    FROM information_schema.tables 
                    WHERE table_name = '{table_name}'
                );
                """
            )
            table_exists = cursor.fetchone()[0]

            if table_exists:
                logger.info(f"✅ Table '{table_name}' already exists.")
                return  # Exit the method early if the table exists

            # Construct the CREATE TABLE SQL query dynamically
            columns_str = ", ".join([f"{col} {dtype}" for col, dtype in columns.items()])
            create_table_query = f"CREATE TABLE {table_name} ({columns_str});"

            # Execute the query
            cursor.execute(create_table_query)
            connection.commit()
            logger.info(f"✅ Table '{table_name}' created successfully.")

        except Exception as e:
            logger.error(f"❌ Error creating table '{table_name}': {e}")
        finally:
            if connection:
                connection.close()
                logger.info("🔌 Connection closed.")

    @classmethod
    def remove_duplicates(cls, table_name: str, columns: list):
        """
        Remove duplicate records from a table based on specific columns.

        :param table_name: Name of the table to remove duplicates from
        :param columns: List of column names to check for duplicates
        """
        connection = None
        try:
            connection = cls.connect_to_db()
            cursor = connection.cursor()

            # Construct the query to remove duplicates using ROW_NUMBER()
            columns_str = ", ".join(columns)
            remove_duplicates_query = f"""
            WITH duplicates AS (
                SELECT 
                    ctid, 
                    ROW_NUMBER() OVER (PARTITION BY {columns_str} ORDER BY ctid) AS row_num
                FROM {table_name}
            )
            DELETE FROM {table_name} 
            WHERE ctid IN (
                SELECT ctid FROM duplicates WHERE row_num > 1
            );
            """

            # Execute the query
            cursor.execute(remove_duplicates_query)
            connection.commit()
            logger.info(f"✅ Duplicates removed from '{table_name}'.")

        except Exception as e:
            logger.error(f"❌ Error removing duplicates from '{table_name}': {e}")
        finally:
            if connection:
                connection.close()
                logger.info("🔌 Connection closed.")
#
# # example
# PostgresDriver.create_table("amin_test", {
#     "id": "SERIAL PRIMARY KEY",
#     "name": "VARCHAR(100)",
#     "email": "VARCHAR(100)",
#     "age": "INT"
# })
