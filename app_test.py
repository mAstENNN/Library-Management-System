import psycopg2
import pytest
import bcrypt


# todo
# def add_new_address(conn, email):
# def delete_clients(conn):  //arsd to test
# def add_new_address(conn, email):
# def display_and_choose_address(conn, email, ask_for_action=False):
# def has_address(conn, email):
# def add_payment_method(conn, email):
# def update_address(conn, email, address):
# def delete_address(conn, email, address):
# def borrow_documents(conn, email):
# def return_documents(conn, email):
# def pay_overdue_fee(conn, email):
# def insert_new_documents(conn):
# def update_existing_documents(conn):
# def search_for_documents():
# def update_client_information(conn, email):
# def update_payment_method(conn, email, payment_method):



# Establish a database connection to your test database
@pytest.fixture(scope="module")
def db_connection():
    connection = psycopg2.connect(
        dbname='cs480', 
        user='postgres', 
        password='test', 
        host='localhost'
    )
    yield connection
    connection.close()


def test_tables_exist(db_connection):
    expected_tables = [
        'address', 'article', 'book', 'borrows', 'client',
        'document', 'librarian', 'magazine', 'payment_method', 'written_by'
    ]
    with db_connection.cursor() as cursor:
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        tables = [row[0] for row in cursor.fetchall()]
        for table in expected_tables:
            assert table in tables, f"Table {table} is missing in the database"


def test_address_table_structure(db_connection):
    expected_columns = {
        'email': 'character varying', 
        'number': 'integer', 
        'street': 'character varying', 
        'city': 'character varying', 
        'state': 'character varying', 
        'zip': 'integer'
    }
    with db_connection.cursor() as cursor:
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'address'""")
        columns = {row[0]: row[1] for row in cursor.fetchall()}
        for column, data_type in expected_columns.items():
            assert column in columns, f"Column {column} is missing in table 'address'"
            assert columns[column] == data_type, f"Data type for {column} in 'address' is not correct"


def test_primary_keys(db_connection):
    with db_connection.cursor() as cursor:
        cursor.execute("""
            SELECT kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_name = 'address' AND tc.constraint_type = 'PRIMARY KEY'
        """)
        primary_keys = {row[0] for row in cursor.fetchall()}
        expected_keys = {'email', 'number', 'street', 'city', 'state', 'zip'}
        assert primary_keys == expected_keys, "Primary key set for 'address' does not match"

def test_foreign_keys(db_connection):
    with db_connection.cursor() as cursor:
        cursor.execute("""
            SELECT tc.constraint_name, kcu.column_name, ccu.table_name AS foreign_table_name, ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name = tc.constraint_name
            WHERE tc.table_name = 'borrows' AND tc.constraint_type = 'FOREIGN KEY'
        """)
        fk_details = {(row[1], row[2]) for row in cursor.fetchall()}
        expected_fks = {('email', 'client'), ('id', 'document')}
        assert fk_details == expected_fks, "Foreign key set for 'borrows' does not match"




@pytest.fixture(autouse=True)
def run_around_tests(db_connection):
    yield
    with db_connection.cursor() as cursor:
        cursor.execute("DELETE FROM address")
        cursor.execute("DELETE FROM client")
        cursor.execute("DELETE FROM article")
        cursor.execute("DELETE FROM document")


def test_insert_client(db_connection):
    with db_connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO public.client (email, first_name, last_name)
            VALUES ('testclient@example.com', 'John', 'Doe');
        """)
        cursor.execute("SELECT * FROM client WHERE email='testclient@example.com'")
        result = cursor.fetchone()
        assert result is not None, "Insertion into client failed"

def test_insert_address_with_foreign_key(db_connection):
    with db_connection.cursor() as cursor:
 
        cursor.execute("""
            INSERT INTO public.client (email, first_name, last_name)
            VALUES ('testclient@example.com', 'John', 'Doe');
        """)
       
        cursor.execute("""
            INSERT INTO public.address (email, number, street, city, state, zip)
            VALUES ('testclient@example.com', 123, 'Main St', 'Anytown', 'Anystate', 12345);
        """)
        cursor.execute("SELECT * FROM address WHERE email='testclient@example.com'")
        result = cursor.fetchone()
        assert result is not None, "Insertion into address failed"


@pytest.fixture
def setup_db(db_connection):
    with db_connection.cursor() as cursor:
  
        cursor.execute("DELETE FROM librarian;")
        cursor.execute("DELETE FROM client;")

        hashed_password_librarian = bcrypt.hashpw(b'secretlib', bcrypt.gensalt()).decode('utf-8')
        hashed_password_client = bcrypt.hashpw(b'secretcli', bcrypt.gensalt()).decode('utf-8')

        cursor.execute("""
            INSERT INTO public.librarian (ssn, first_name, last_name, email, password)
            VALUES (%s, %s, %s, %s, %s)""",
            ('123-45-6789', 'xer', 'frh', 'librarian@example.com', hashed_password_librarian))
   
        cursor.execute("""
            INSERT INTO public.client (email, first_name, last_name, password)
            VALUES (%s, %s, %s, %s)""",
            ('client@example.com', 'Jane', 'Doe', hashed_password_client))
    db_connection.commit()




from app import verify_credentials

def test_verify_credentials_librarian_success(db_connection, setup_db):
    assert verify_credentials('librarian@example.com', 'secretlib', db_connection) == 'librarian', \
        "Should successfully authenticate librarian with correct password"

def test_verify_credentials_client_success(db_connection, setup_db):
    assert verify_credentials('client@example.com', 'secretcli', db_connection) == 'client', \
        "Should successfully authenticate client with correct password"

def test_verify_credentials_incorrect_password(db_connection, setup_db):
    assert verify_credentials('librarian@example.com', 'wrongpassword', db_connection) is None, \
        "Should fail to authenticate with incorrect password"

def test_verify_credentials_nonexistent_user(db_connection, setup_db):
    assert verify_credentials('nonexistent@example.com', 'password', db_connection) is None, \
        "Should return None for non-existent user"


from unittest.mock import MagicMock
class ConnectionWrapper:
    def __init__(self, real_connection):
        self._real_connection = real_connection
        self._mock_cursor = None

    def cursor(self):
  
        if self._mock_cursor:
            return self._mock_cursor
        return self._real_connection.cursor()

    def set_mock_cursor(self, mock_cursor):
        self._mock_cursor = mock_cursor

    def __getattr__(self, item):

        return getattr(self._real_connection, item)

@pytest.fixture
def db_connection_wrapper(db_connection):

    return ConnectionWrapper(db_connection)

def test_verify_credentials_error_handling(db_connection_wrapper, setup_db, monkeypatch):

    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = psycopg2.DatabaseError("Simulated database error")
    

    db_connection_wrapper.set_mock_cursor(mock_cursor)

    assert verify_credentials('librarian@example.com', 'secretlib', db_connection_wrapper) is None, \
        "Should handle database errors gracefully"




def has_borrowed_documents(conn, email):
    cur = conn.cursor()
    try:
   
        cur.execute("""
            SELECT COUNT(*)
            FROM public.borrows
            WHERE email = %s AND return_date IS NULL
        """, (email,))
        result = cur.fetchone() 

      
        if result[0] > 0:
            return True
        else:
            return False
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        return False
    finally:
        cur.close()



def has_borrowed_documents(conn, email):
    cur = conn.cursor()
    try:
   
        cur.execute("""
            SELECT COUNT(*)
            FROM public.borrows
            WHERE email = %s AND return_date IS NULL
        """, (email,))
        result = cur.fetchone()  

   
        if result[0] > 0:
            return True
        else:
            return False
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        return False
    finally:
        cur.close()


def test_has_borrowed_documents_with_unreturned_items(db_connection):
    with db_connection.cursor() as cursor:
        cursor.execute("INSERT INTO client (email, first_name, last_name) VALUES ('testuser@example.com', 'Test', 'User')")
        cursor.execute("INSERT INTO document (id, type) VALUES (1, 'Book')")
        cursor.execute("INSERT INTO borrows (email, id, borrow_date) VALUES ('testuser@example.com', 1, CURRENT_DATE)")
        db_connection.commit()

        assert has_borrowed_documents(db_connection, 'testuser@example.com') == True, "Should detect unreturned documents"

def test_has_borrowed_documents_with_all_returned(db_connection):
    with db_connection.cursor() as cursor:
 
        cursor.execute("INSERT INTO client (email, first_name, last_name) VALUES ('testuser@example.com', 'Test', 'User')")
        cursor.execute("INSERT INTO document (id, type) VALUES (1, 'Book')")
        cursor.execute("INSERT INTO borrows (email, id, borrow_date, return_date) VALUES ('testuser@example.com', 1, CURRENT_DATE, CURRENT_DATE)")
        db_connection.commit()

        assert has_borrowed_documents(db_connection, 'testuser@example.com') == False, "Should not detect any unreturned documents"

def test_has_borrowed_documents_no_borrows(db_connection):
    with db_connection.cursor() as cursor:

        cursor.execute("INSERT INTO client (email, first_name, last_name) VALUES ('newuser@example.com', 'New', 'User')")
        db_connection.commit()

        assert has_borrowed_documents(db_connection, 'newuser@example.com') == False, "Should handle users with no borrowed documents"





def test_register_new_client(db_connection):
    """Test the registration of a new client by inserting into the database and verifying."""
    email = "test@example.com"
    first_name = "Test"
    last_name = "User"
    password = "securepassword123"
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    cur = db_connection.cursor()
    try:
        cur.execute("""
            INSERT INTO public.client (email, first_name, last_name, overdue_fee, password)
            VALUES (%s, %s, %s, %s, %s)
        """, (email, first_name, last_name, 0.00, hashed_password))
        db_connection.commit()


        cur.execute("SELECT * FROM public.client WHERE email = %s", (email,))
        result = cur.fetchone()
        assert result is not None, "Client was not successfully registered"
        assert result[1] == first_name, "First name does not match"
        assert result[2] == last_name, "Last name does not match"
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        db_connection.rollback()
        pytest.fail(f"Database error during registration: {e}")
    finally:
        cur.close()

        cur = db_connection.cursor()
        cur.execute("DELETE FROM public.client WHERE email = %s", (email,))
        db_connection.commit()
        cur.close()


# has_payment_method
from datetime import datetime, timedelta

def setup_payment_method_data(db_connection, email, has_payment):
    """Helper function to insert or not insert payment method data based on has_payment flag."""
    cur = db_connection.cursor()
    try:
        cur.execute("DELETE FROM public.payment_method WHERE email = %s", (email,)) 
        if has_payment:

            cur.execute("INSERT INTO public.client (email, first_name, last_name) VALUES (%s, %s, %s)", (email, "Test", "User"))
  
            cur.execute("""
                INSERT INTO public.payment_method (email, card_number, company, exp_date)
                VALUES (%s, %s, %s, %s)
            """, (email, "1234567890123456", "Test Bank", datetime.now().date() + timedelta(days=365)))
        db_connection.commit()
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        db_connection.rollback()
    finally:
        cur.close()

def test_has_payment_method_true(db_connection):
    email = "test@example.com"
    setup_payment_method_data(db_connection, email, True)
    from app import has_payment_method  
    assert has_payment_method(db_connection, email) == True, "Function should return True when payment methods exist"

def test_has_payment_method_false(db_connection):
    email = "no_payment@example.com"
    setup_payment_method_data(db_connection, email, False)
    from app import has_payment_method 
    assert has_payment_method(db_connection, email) == False, "Function should return False when no payment methods exist"


# display_and_choose_payment_method
# Setup function for testing

def setup_payment_method_data(db_connection, email, has_payment):
    """
    Sets up or removes payment method data for a given email based on the has_payment flag.
    
    Args:
    db_connection : database connection object
    email : str, the email address associated with the client
    has_payment : bool, determines whether to insert or remove payment data
    """
    cur = db_connection.cursor()
    try:
      
        cur.execute("DELETE FROM public.payment_method WHERE email = %s", (email,))
        cur.execute("DELETE FROM public.client WHERE email = %s", (email,))
        
        if has_payment:
         
            cur.execute("INSERT INTO public.client (email, first_name, last_name) VALUES (%s, 'Test', 'User')", (email,))
            

            cur.execute("""
                INSERT INTO public.payment_method (email, card_number, company, exp_date)
                VALUES (%s, %s, %s, %s)
            """, (email, '1234567890123456', 'Test Bank', datetime.now() + timedelta(days=365)))
        
        db_connection.commit()
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        db_connection.rollback()
    finally:
        cur.close()


def test_setup_payment_method_insert(db_connection):
    email = "insert_test@example.com"
    setup_payment_method_data(db_connection, email, True)
    cur = db_connection.cursor()
    cur.execute("SELECT * FROM public.client WHERE email = %s", (email,))
    client_result = cur.fetchone()
    cur.execute("SELECT * FROM public.payment_method WHERE email = %s", (email,))
    payment_method_result = cur.fetchone()
    assert client_result is not None
    assert payment_method_result is not None
    assert payment_method_result[1] == '1234567890123456' 

#
def test_setup_payment_method_remove(db_connection):
    email = "remove_test@example.com"

    setup_payment_method_data(db_connection, email, True)

    setup_payment_method_data(db_connection, email, False)
    cur = db_connection.cursor()
    cur.execute("SELECT * FROM public.client WHERE email = %s", (email,))
    client_result = cur.fetchone()
    cur.execute("SELECT * FROM public.payment_method WHERE email = %s", (email,))
    payment_method_result = cur.fetchone()
    assert client_result is None
    assert payment_method_result is None


# def delete_payment_method(conn, email, payment_method):
from app import delete_payment_method

@pytest.fixture
def setup_payment_method(db_connection):
    email = "test@example.com"
    card_number = "9876543210987654"
    cur = db_connection.cursor()
    cur.execute("INSERT INTO public.client (email, first_name, last_name) VALUES (%s, 'Test', 'User')", (email,))
    cur.execute("INSERT INTO public.payment_method (email, card_number, company, exp_date) VALUES (%s, %s, 'Test Bank', '2025-12-31')", (email, card_number))
    db_connection.commit()
    yield email, card_number
    cur.execute("DELETE FROM public.payment_method WHERE email = %s", (email,))
    cur.execute("DELETE FROM public.client WHERE email = %s", (email,))
    db_connection.commit()
    cur.close()


def test_delete_payment_method(db_connection, setup_payment_method):
    email, card_number = setup_payment_method
    delete_payment_method(db_connection, email, [card_number])
    cur = db_connection.cursor()
    cur.execute("SELECT * FROM public.payment_method WHERE email = %s AND card_number = %s", (email, card_number))
    result = cur.fetchone()
    assert result is None 


from app import delete_clients

# from unittest.mock import patch
# @pytest.fixture
# def setup_delete_clients(db_connection):
#     email = "test@example.com"
#     overdue_fee = 0
#     cur = db_connection.cursor()
#     try:
#         cur.execute("INSERT INTO public.client (email, first_name, last_name, overdue_fee) VALUES (%s, 'Test', 'User', %s)", (email, overdue_fee))
#         db_connection.commit()
#         yield email, overdue_fee
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         db_connection.rollback()
#     finally:
    
#         cur.execute("DELETE FROM public.client WHERE email = %s", (email,))
#         db_connection.commit()
#         cur.close()



