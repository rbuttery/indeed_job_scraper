import os
import sqlite3
import pandas as pd

from logger_config import logger 
# logger.basicConfig(filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.log'), level=format='%(asctime)s - %(levelname)s - %(message)s')


class DatabaseTools:
    def __init__(self):
        self.db_name = 'indeed.db'
        self.current_directory = os.path.dirname(os.path.abspath(__file__))
        self.database_path = os.path.join(self.current_directory, self.db_name)
        self.ddl_path = os.path.join(self.current_directory, 'ddl.sql')
        self.ddl = None
        self.setup()
        logger.info('-'*50)
        logger.info(f'DatabaseTools initialized with database: {self.database_path}')
        
    def connect(self):
        self.conn = sqlite3.connect(self.database_path)
        self.cursor = self.conn.cursor()
    
    def setup(self, force_update=True):
        def create_new():
            logger.info(f'Reading DDL file: {self.ddl_path}')
            try:
                with open(self.ddl_path, 'r') as f:
                    self.ddl = f.read()
            except FileNotFoundError:
                logger.error(f'DDL file not found: {self.ddl_path}')
                exit()

            logger.info(f'Setting up database: {self.database_path}')
            try:
                self.connect()
                self.cursor.executescript(self.ddl) 
                self.conn.commit()
            except sqlite3.Error as e:
                logger.ERROR(f'Error setting up database: {e}')
                exit()
        # First check if the database already exists.
        if force_update:
            create_new()
            logger.info(f'Force update: Database created: {self.database_path}')
        elif os.path.exists(self.database_path):
            logger.info(f'Database already exists: {self.database_path}')
        else:
            create_new()
            logger.info(f'Database created: {self.database_path}')
    
    def run_sql(self, sql): 
        self.connect()
        self.cursor.execute(sql)
        tables = self.cursor.fetchall()
        self.conn.commit()
        self.conn.close()
        return tables
              
    def list_tables(self):
        print(f'Listing tables in database: {self.database_path}')
        self.connect()
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.cursor.fetchall()
        self.conn.close()
        try:
            return [x[0] for x in tables]
        except IndexError:
            raise Exception('No tables found in database.')
        
    def sql_to_df(self, sql):
        self.connect()
        self.cursor.execute(sql)
        data = self.cursor.fetchall()
        columns = [column[0] for column in self.cursor.description]
        self.conn.close()
        try:
            return pd.DataFrame(data, columns=columns)
        except ValueError:
            raise Exception('No data found.')
        
    def insert_record(self, table_name, data):
        """Inserts a record into any table based on the provided data dictionary."""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        sql = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'
        
        self.connect()
        try:
            self.cursor.execute(sql, tuple(data.values()))
            self.conn.commit()
            print(f"Record successfully inserted into {table_name}.")
        except sqlite3.Error as e:
            print(f'Error inserting record into {table_name}:', e)
        finally:
            self.conn.close()

        
    def start_new_session(self, terms, location, filter_tags='', n_pages=None):
        """Starts a new search session with given parameters and saves it to the database."""
        ended_at = None  # This can be updated when the session ends.
        
        try:
            self.connect()
            self.cursor.execute(
                "INSERT INTO search_sessions (terms, location, filter_tags, n_pages, ended_at) VALUES (?, ?, ?, ?, ?)",
                (terms, location, filter_tags, n_pages, ended_at)
            )
            self.conn.commit()
            session_id = self.cursor.lastrowid
            print(f"New session started with ID: {session_id}")
            return session_id
        except sqlite3.Error as e:
            print('Error starting new session:', e)
        finally:
            self.conn.close()
    
    def update_job_postings(self, obj):
        obj_id = obj['job_unique_id']
        print(f'Updating job postings with id: {obj_id}')
        self.connect()
        self.cursor.execute('''
            INSERT OR IGNORE INTO job_postings (
                job_unique_id, 
                job_title, 
                job_link, 
                session_id, 
                job_company
                )
            VALUES (?, ?, ?, ?, ?)
        ''', (obj['job_unique_id'], obj['job_title'], obj['job_link'], obj['session_id'], obj['job_company']))
        self.conn.commit()
        
    def get_postings_by_session(self, session_id):
        sql = f'''
            SELECT * FROM job_postings
            WHERE session_id = {session_id}
        '''
        return self.sql_to_df(sql)
    
    def update_job_posting_description(self, job_unique_id, description):
        self.connect()
        self.cursor.execute('''
            UPDATE job_postings
            SET job_description = ?
            WHERE job_unique_id = ?
        ''', (description, job_unique_id))
        self.conn.commit()
        self.conn.close()
        
    def insert_job_detail(self, job_detail):
        """Inserts a job detail record into the job_details table from a dictionary."""
        print(f'Inserting job id {job_detail["job_unique_id"]} into job_details table.')
        self.connect()
        try:
            # Convert lists to comma-separated strings
            for key, value in job_detail.items():
                if isinstance(value, list):
                    job_detail[key] = ', '.join(value)
            
            # Prepare columns and placeholders for SQL statement
            columns = ', '.join(job_detail.keys())
            placeholders = ', '.join(['?' for _ in job_detail])
            
            # Build and execute the SQL statement
            sql = f'INSERT INTO job_details ({columns}) VALUES ({placeholders})'
            self.cursor.execute(sql, tuple(job_detail.values()))
            self.conn.commit()
            print("Job details successfully inserted.")
        except sqlite3.Error as e:
            print('Error inserting job detail:', e)
        finally:
            self.conn.close()
            
    def list_tables(self):
        print(f'Listing tables in database: {self.database_path}')
        self.connect()
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.cursor.fetchall()
        self.conn.close()
        try:
            return [x[0] for x in tables]
        except IndexError:
            raise Exception('No tables found in database.')

    
    
        
