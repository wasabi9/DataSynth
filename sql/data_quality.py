import os
import psycopg2
from psycopg2.errors import DuplicateDatabase, DuplicateTable
import json
from tqdm import tqdm

db_user = "postgres"
db_password = "postgres"
db_host = "localhost"
db_port = "5432"

def create_database(db_name: str):
    # connection establishment
    conn = psycopg2.connect(
    database="postgres",
        user='postgres',
        password='postgres',
        host='localhost',
        port= '5432'
    )
    
    conn.autocommit = True
    
    # Creating a cursor object
    cursor = conn.cursor()

    try:
        sql = ''' CREATE database {0};'''.format(db_name)
        cursor.execute(sql)
    except DuplicateDatabase:
        return
    conn.close()

# Read the SQL file
def read_sql_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()
    
# Function to create a connection to the database
def create_connection(db_name, db_user, db_password, db_host, db_port):
    connection = None
    try:
        connection = psycopg2.connect(
            database=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
        )
        # print("Connection to PostgreSQL DB successful")
    except Exception as e:
        # import ipdb; ipdb.set_trace()
        print(f"The error '{e}' occurred")
    return connection
    
# Function to execute an SQL query
def execute_query(connection, query):
    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        # print("Query executed successfully")
        return None
    except DuplicateTable:
        return None
    except Exception as e:
        print(f"The error '{e}' occurred")
        return str(e)

def setup_databases(folder, qc_log_file):
    error_log = {}
    for ddl_file in tqdm(os.listdir(folder)):
        # import ipdb; ipdb.set_trace()
        db_name = ddl_file.split('.')[0].lower()
        print("setting up {0}".format(ddl_file))

        create_database(db_name)
        connection = create_connection(db_name, db_user, db_password, db_host, db_port)

        ddl_content = read_sql_file(os.path.join(folder, ddl_file))
        
        error = execute_query(connection, ddl_content)

        if error is not None:
            error_log[ddl_file] = error

        # break

    with open(os.path.join("/Users/abhinaykumar/Desktop/Work/featherflow/llama-tests/datasets/qc_logs",qc_log_file+".json"), "w") as qc_file:
        json.dump(error_log, qc_file)    
                

def check_questions(folder, qc_log_file):
    import ipdb; ipdb.set_trace()
    files = os.listdir(folder)
    qc_logs = {}
    for file in files:
        db_name = file.split(".")[0].lower()

        qc_logs[file] = {}

        with open(os.path.join(folder, file), "r") as question_file:
            questions = json.load(question_file)

        connection = create_connection(db_name, db_user, db_password, db_host, db_port)

        for question in questions:
            query = questions[question]
            error = execute_query(connection, query)

            if error is not None:
                qc_logs[file][query] = error
    
    with open(os.path.join("/Users/abhinaykumar/Desktop/Work/featherflow/llama-tests/datasets/qc_logs",qc_log_file+".json"), "w") as qc_file:
        json.dump(qc_logs, qc_file)

if __name__ == "__main__":
    # folder = "/Users/abhinaykumar/Desktop/Work/featherflow/llama-tests/datasets/created_v2"
    # qc_log_file = "test_v2"
    # setup_databases(folder, qc_log_file)

    folder = "/Users/abhinaykumar/Desktop/Work/featherflow/llama-tests/datasets/metadata_v2/questions"
    qc_log_file = "questions_v2"
    check_questions(folder, qc_log_file)