import os
import MySQLdb
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """Opens a new connection to the Aiven MySQL database."""
    return MySQLdb.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        passwd=os.getenv("DB_PASSWORD"),
        db=os.getenv("DB_NAME"),
        # ssl_mode="VERIFY_IDENTITY",
        # ssl={"ca": os.getenv("DB_SSL_CA")},
    )


def authenticate_employee(Email: str, Emp_ID: str):
    """
    Verifies login credentials and returns the employee's data if valid,
    or None if not found / credentials don't match.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)  # returns rows as dicts

        query = """
            SELECT *
            FROM emp_table
            WHERE Email = %s AND Emp_ID = %s
        """
        cursor.execute(query, (Email, Emp_ID))
        result = cursor.fetchone()
        cursor.close()
        return result  # dict or None

    except MySQLdb.Error as e:
        print(f"Database error: {e}")
        return None

    finally:
        if conn:
            conn.close()

#querying data
# def get_data(Email: str, Emp_ID: str):
#     conn = None
#     try:
#         conn = get_connection()
#         cursor = conn.cursor(MySQLdb.cursors.DictCursor)

#         query = "SELECT Name FROM emp_table WHERE Email = %s AND Emp_ID = %s"

#         cursor.execute(query, (Email, Emp_ID))
#         Name = cursor.fetchone()
#         cursor.close()
#         return Name
#     except MySQLdb.Error as e:
#         print(f"Error: {e}")
#         return None
#     finally:
#         if conn:
#             conn.close()

def submit_complaint(subject_field: str, description_field: str, emp_id: str):
    """
    Inserts a new complaint into the database.
    Returns True on success, False on failure.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO complaints (Emp_ID, subject_field, description_field)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (emp_id, subject_field, description_field))
        conn.commit()
        cursor.close()
        return True

    except MySQLdb.Error as e:   # or mysql.connector.Error, depending on your driver
        print(f"Database error: {e}")
        return False

    finally:
        if conn:
            conn.close()


def submit_leave(leave_type: str, reason: str, emp_id: str):
    """
    Inserts a new leave application into the database.
    Returns True on success, False on failure.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO leave_applications (leave_type, reason, Emp_ID)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (leave_type, reason, emp_id))
        conn.commit()
        cursor.close()
        return True

    except MySQLdb.Error as e:   # or mysql.connector.Error, depending on your driver
        print(f"Database error: {e}")
        return False

    finally:
        if conn:
            conn.close()