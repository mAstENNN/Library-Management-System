# %%
import psycopg2
import bcrypt
from getpass import getpass  # For secure password input
import datetime

def connect():
    # Connect to your PostgreSQL database
    conn = psycopg2.connect(
        # dbname='project', 
        # user='postgres', 
        # password='Sm0020420293', 
        # host='localhost'

        dbname='cs480', 
        user='postgres', 
        password='test', 
        host='localhost'
    )
    return conn

# Function to verify the user's credentials and determine their role
def verify_credentials(email, password, conn):
    # Initialize role as None
    user_role = None
    cur = conn.cursor()
    try:
        # Try to fetch from the librarian table
        cur.execute("SELECT password FROM public.librarian WHERE email = %s", (email,))
        librarian_hashed_password = cur.fetchone()
        
        # Try to fetch from the client table
        cur.execute("SELECT password FROM public.client WHERE email = %s", (email,))
        client_hashed_password = cur.fetchone()

        # Check librarian table
        if librarian_hashed_password and bcrypt.checkpw(password.encode('utf-8'), librarian_hashed_password[0].encode('utf-8')):
            user_role = 'librarian'
        # Check client table
        elif client_hashed_password and bcrypt.checkpw(password.encode('utf-8'), client_hashed_password[0].encode('utf-8')):
            user_role = 'client'

        # Evaluate authentication and role assignment
        if user_role:
            print(f"Login successful. Role: {user_role}")
            return user_role
        else:
            print("Login failed. Incorrect email or password.")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        cur.close()

def has_borrowed_documents(conn, email):
    cur = conn.cursor()
    try:
        # SQL query to find any borrowed documents with no return date
        cur.execute("""
            SELECT COUNT(*)
            FROM public.borrows
            WHERE email = %s AND return_date IS NULL
        """, (email,))
        result = cur.fetchone()  # Fetch the result of the count query

        # If the count is greater than 0, there are unreturned documents
        if result[0] > 0:
            return True
        else:
            return False
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        return False
    finally:
        cur.close()

def register_new_client(conn):
    print("Registering a new client...")
    
    # Collect client information
    email = input("Enter client's email: ")
    first_name = input("Enter client's first name: ")
    last_name = input("Enter client's last name: ")
    # Assuming the overdue_fee is initially 0 for all new clients
    overdue_fee = 0.00
    password = input("Enter client's password: ")
    
    # Hash the password
    # hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    # small fix mas
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    # SQL to insert the new client
    insert_sql = """
    INSERT INTO public.client (email, first_name, last_name, overdue_fee, password)
    VALUES (%s, %s, %s, %s, %s)
    """
    
    cur = conn.cursor()
    try:
        # Execute the SQL command
        cur.execute(insert_sql, (email, first_name, last_name, overdue_fee, hashed_password))
        conn.commit()  # Commit the transaction
        print("New client registered successfully.")
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()  # Roll back the transaction on error
    finally:
        cur.close()

def has_payment_method(conn, email):
    cur = conn.cursor()
    cur.execute("""
        SELECT card_number, company, exp_date
        FROM public.payment_method
        WHERE email = %s
    """, (email,))
    payment_methods = cur.fetchall()

    if payment_methods:
        return True
    else:
        print("No payment methods found for this client.")
        return False

def display_and_choose_payment_method(conn, email, ask_for_action=False):
    cur = conn.cursor()
    cur.execute("""
        SELECT card_number, company, exp_date
        FROM public.payment_method
        WHERE email = %s
    """, (email,))
    payment_methods = cur.fetchall()

    print("\nClient's Payment Methods:")
    for idx, (card_number, company, exp_date) in enumerate(payment_methods, start=1):
        print(f"{idx}. Card Number: {card_number}, Company: {company}, Expiration Date: {exp_date}")
    
    if ask_for_action:
        choice = input("Choose a payment method to update/delete (or type 'cancel' to return): ")
        if choice.lower() == 'cancel':
            return None, 'cancel'
    else:
        choice = input("Choose a payment method: ")
    
    try:
        chosen_index = int(choice) - 1
        if chosen_index >= len(payment_methods) or chosen_index < 0:
            print("Invalid choice.")
            return None, 'cancel'
    except ValueError:
        print("Invalid input.")
        return None, 'cancel'

    action = None
    if ask_for_action:
        action = input("Do you want to update or delete this payment method? (update/delete): ").lower()
        if action not in ['update', 'delete']:
            print("Invalid action.")
            return None, 'cancel'

    return payment_methods[chosen_index], action

def update_client_information(conn, email):
    print("Updating client information...")
    
    option_descriptions = {
        '1': "First Name",
        '2': "Last Name",
        '3': "Password",
        '4': "Address",
        '5': "Paymeny Method",
        '6': "Finish updating"
    }
    
    update_data = {}
    column_mapping = {
        '1': 'first_name',
        '2': 'last_name',
        '3': 'password',
    }
    while True:
        print("\nWhat would you like to update?")
        for key, value in option_descriptions.items():
            print(f"{key}. {value}")
            
        choice = input("Select an option: ")
        if choice in ['1', '2', '3']:
            new_value = input(f"Enter the new {option_descriptions[choice].lower()}: ")
            if choice == '3':
                new_value = bcrypt.hashpw(new_value.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            update_data[column_mapping[choice]] = new_value
        elif choice == '4':
            if has_address(conn, email):
                address, action = display_and_choose_address(conn, email, ask_for_action=True)
                if action == 'update':
                    update_address(conn, email, address)
                elif action == 'delete':
                    delete_address(conn, email, address)
        elif choice == '5':
            if has_payment_method(conn, email):
                payment_method, action = display_and_choose_payment_method(conn, email, ask_for_action=True)
                if action == 'update':
                    update_payment_method(conn, email, payment_method)
                elif action == 'delete':
                    delete_payment_method(conn, email, payment_method)
        elif choice == '6':
            break
        else:
            print("Invalid option. Please try again.")
        
    # Update the client's information in the database
    cur = conn.cursor()
    try:
        for key, value in update_data.items():
            cur.execute(f"UPDATE public.client SET {key} = %s WHERE email = %s", (value, email))
        conn.commit()
        print("Client information updated successfully.")
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()  # Roll back the transaction on error
    finally:
        cur.close()

def delete_payment_method(conn, email, payment_method):
    print("Deleting payment method...")
    card_number = payment_method[0]
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM public.payment_method WHERE email = %s AND card_number = %s", (email, card_number))
        conn.commit()
        print("Payment method deleted successfully.")
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        cur.close()
    
def update_payment_method(conn, email, payment_method):
    print("Updating payment method...")
    card_number = payment_method[0]
    
    update_options = {
        '1': "Card Number",
        '2': "CVV",
        '3': "Company",
        '4': "Expiration Date",
        '5': "Associated Address",
        '6': "Finish updating"
    }
    
    update_data = {}
    column_mapping = {
        '1': 'card_number',
        '2': 'CVV',
        '3': 'company',
        '4': 'exp_date'
    }
    while True:
        print("\nWhat attribute do you want to update?")
        for key, value in update_options.items():
            print(f"{key}. {value}")
        choice = input("Select an option: ")
        
        if choice == '6':
            break  # Exit the update loop
        
        if choice in ['1', '2', '3', '4']:
            new_value = input(f"Enter the new {update_options[choice].lower()}: ")
            update_data[column_mapping[choice]] = new_value
        elif choice == '5':  # Address Update
            chosen_address, _ = display_and_choose_address(conn, email)
            if chosen_address:
                number, street, city, state, zip_code = chosen_address
                update_data['number'] = number
                update_data['street'] = street
                update_data['city'] = city
                update_data['state'] = state
                update_data['zip'] = zip_code
        else:
            print("Invalid option. Please try again.")
    
    # Apply all updates
    cur = conn.cursor()
    try:
        for key, value in update_data.items():
            cur.execute(f"UPDATE public.payment_method SET {key} = %s WHERE email = %s AND card_number = %s", (value, email, card_number))
        conn.commit()
        print("Payment method updated successfully.")
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        cur.close()

def delete_clients(conn):
    print("Deleting a client...")
    
    email = input("Enter the client's email to delete: ")
    
    # First, check for overdue fee
    cur = conn.cursor()
    try:
        cur.execute("SELECT overdue_fee FROM public.client WHERE email = %s", (email,))
        result = cur.fetchone()
        
        # Check if client exists
        if result is None:
            print("No client found with that email.")
            return
        
        overdue_fee = result[0]
        
        # Check for overdue fee and borrowed documents
        if overdue_fee > 0:
            print("Cannot delete client with an overdue fee.")
        elif has_borrowed_documents(email, conn):
            print("Cannot delete client with borrowed documents.")
        else:
            # Proceed to delete the client
            cur.execute("DELETE FROM public.client WHERE email = %s", (email,))
            conn.commit()
            print("Client deleted successfully.")
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()  # Roll back the transaction on error
    finally:
        cur.close()

def add_new_address(conn, email):
    print("Adding new address...")
    # Collect address information from user
    number = input("Enter the address number: ")
    street = input("Enter the street: ")
    city = input("Enter the city: ")
    state = input("Enter the state: ")
    zip_code = input("Enter the ZIP code: ")
    
    # SQL statement for inserting the new address
    insert_sql = """
    INSERT INTO public.address (email, "number", street, city, state, zip)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    cur = conn.cursor()
    try:
        cur.execute(insert_sql, (email, number, street, city, state, zip_code))
        conn.commit()  # Commit the transaction
        print("New address added successfully.")
    except psycopg2.Error as e:
        print(f"An error occurred while adding the new address: {e}")
        conn.rollback()  # Roll back the transaction on error
    finally:
        cur.close()
    
def display_and_choose_address(conn, email, ask_for_action=False):
    cur = conn.cursor()
    cur.execute("""
        SELECT "number", street, city, state, zip
        FROM public.address
        WHERE email = %s
    """, (email,))
    addresses = cur.fetchall()

    print("\nClient's Addresses:")
    for idx, address in enumerate(addresses, start=1):
        number, street, city, state, zip_code = address
        print(f"{idx}. {number}, {street}, {city}, {state}, {zip_code}")
    
    if ask_for_action:
        choice = input("Choose an address to update/delete (or type 'cancel' to return): ")
        if choice.lower() == 'cancel':
            return None, 'cancel'
    else:
        choice = input("Choose an address for the payment method: ")
    
    try:
        chosen_index = int(choice) - 1
        if chosen_index >= len(addresses) or chosen_index < 0:
            print("Invalid choice.")
            return None, 'cancel'
    except ValueError:
        print("Invalid input.")
        return None, 'cancel'

    action = None
    if ask_for_action:
        action = input("Do you want to update or delete this address? (update/delete): ").lower()
        if action not in ['update', 'delete']:
            print("Invalid action.")
            return None, 'cancel'
    
    return addresses[chosen_index], action

def has_address(conn, email):
    cur = conn.cursor()
    cur.execute("""
        SELECT "number", street, city, state, zip
        FROM public.address
        WHERE email = %s
    """, (email,))
    addresses = cur.fetchall()
    if addresses:
        return True
    else:
        print("No addresse found for this client.")
        return False

def add_payment_method(conn, email):
    # Check if the user has any addresses
    if not has_address(conn, email):
        print("Please add an address before adding a payment method.")
        return
    
    # Collect payment method information
    card_number = input("Enter card number: ")
    cvv = input("Enter CVV: ")
    exp_date = input("Enter expiration date (YYYY-MM-DD): ")
    company = input("Enter card company: ")
    
    # Choose address for the payment method
    chosen_address, _ = display_and_choose_address(conn, email)
    if not chosen_address:
        print("No address selected for the payment method.")
        return
    
    number, street, city, state, zip_code = chosen_address
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO public.payment_method (email, card_number, "number", street, city, state, zip, "CVV", exp_date, company)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (email, card_number, number, street, city, state, zip_code, cvv, exp_date, company))
        conn.commit()
        print("Payment method added successfully.")
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        cur.close()

def update_address(conn, email, address):
    print("Updating address...")
    number, street, city, state, zip_code = address
    new_number = input("Enter new address number: ")
    new_street = input("Enter new street: ")
    new_city = input("Enter new city: ")
    new_state = input("Enter new state: ")
    new_zip = input("Enter new zip code: ")
    
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE public.address
            SET "number" = %s, street = %s, city = %s, state = %s, zip = %s
            WHERE email = %s AND "number" = %s AND street = %s AND city = %s AND state = %s AND zip = %s
        """, (new_number, new_street, new_city, new_state, new_zip, email, number, street, city, state, zip_code))
        conn.commit()
        print("Address updated successfully.")
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        cur.close()

def delete_address(conn, email, address):
    print("Deleting address...")
    number, street, city, state, zip_code = address
    
    cur = conn.cursor()
    try:
        cur.execute("""
            DELETE FROM public.address
            WHERE email = %s AND "number" = %s AND street = %s AND city = %s AND state = %s AND zip = %s
        """, (email, number, street, city, state, zip_code))
        conn.commit()
        print("Address deleted successfully.")
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        cur.close()
        
def get_email(conn):
    email = input("Enter the client's email: ")
    # Check if the client exists
    cur = conn.cursor()
    cur.execute("SELECT email FROM public.client WHERE email = %s", (email,))
    result = cur.fetchone()
    cur.close()
    if not result:
        return None
    else:
        return email

def borrow_documents(conn, email):
    print("Borrowing documents...")
    
    # Ask the user for the document ID they wish to borrow
    document_id = input("Enter the document ID you wish to borrow: ")

    cur = conn.cursor()
    try:
        # Check if the document exists and if copies are available
        cur.execute("""
            SELECT num_copies FROM public.document WHERE id = %s
        """, (document_id,))
        result = cur.fetchone()

        if not result:
            print("No document found with that ID.")
            return
        
        num_copies = result[0]
        
        # Check if the client already has this document borrowed and not returned
        cur.execute("""
            SELECT id FROM public.borrows WHERE email = %s AND id = %s AND return_date IS NULL
        """, (email, document_id))
        if cur.fetchone():
            print("You have already borrowed this document and have not returned it yet.")
            return

        # Validate against borrowed copies
        cur.execute("SELECT COUNT(*) FROM public.borrows WHERE id = %s AND return_date IS NULL", (doc_id,))
        num_borrowed = cur.fetchone()[0]
        if num_copies <= num_borrowed:
            print("No copies left of this document to borrow.")
            return

        # Record the borrow in the borrows table
        today_date = datetime.date.today()
        cur.execute("""
            INSERT INTO public.borrows (email, id, borrow_date)
            VALUES (%s, %s, %s)
        """, (email, document_id, today_date))

        conn.commit()
        print(f"Document ID {document_id} borrowed successfully on {today_date}. Please return on time.")

    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        cur.close()

def return_documents(conn, email):
    print("Returning documents...")
    cur = conn.cursor()
    try:
        # Fetch all documents along with their titles or names that this user has borrowed but not returned
        cur.execute("""
        SELECT b.id, b.borrow_date, COALESCE(book.title, magazine.name, article.title) AS title
        FROM public.borrows b
        LEFT JOIN public.book ON b.id = book.id
        LEFT JOIN public.magazine ON b.id = magazine.id
        LEFT JOIN public.article ON b.id = article.id
        WHERE b.email = %s AND b.return_date IS NULL
        """, (email,))
        documents = cur.fetchall()

        if not documents:
            print("You have no documents to return.")
            return

        # Display the documents to the user
        print("Documents borrowed by you that haven't been returned yet:")
        for idx, (doc_id, borrow_date, title) in enumerate(documents, 1):
            print(f"{idx}. Document ID: {doc_id}, Title: {title}, Borrowed on: {borrow_date}")

        # Get user input to choose a document to return
        choice = input("Choose the document you wish to return or type 'cancel' to exit: ")
        if choice.lower() == 'cancel':
            print("No document was returned.")
            return

        choice_index = int(choice) - 1
        document_id, borrow_date, _ = documents[choice_index]

        # Set return date and calculate fees
        return_date = datetime.date.today()
        weeks_borrowed = (return_date - borrow_date).days // 7
        fee = 5 * (weeks_borrowed+1)

        # Transaction to update return date and overdue fee
        cur.execute("""
        UPDATE public.borrows
        SET return_date = %s
        WHERE email = %s AND id = %s
        """, (return_date, email, document_id))

        cur.execute("""
        UPDATE public.client
        SET overdue_fee = overdue_fee + %s
        WHERE email = %s
        """, (fee, email))

        conn.commit()
        print(f"Document ID {document_id} returned successfully on {return_date}. Fee charged: ${fee}.")
        
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    except IndexError:
        print("Invalid selection. Please try again.")
    except ValueError:
        print("Invalid input. Please enter a valid number.")
    finally:
        cur.close()

def pay_overdue_fee(conn, email):
    print("Paying overdue fee...")

    cur = conn.cursor()
    try:
        # Retrieve payment methods
        cur.execute("SELECT card_number, company FROM public.payment_method WHERE email = %s", (email,))
        payment_methods = cur.fetchall()
        if not payment_methods:
            print("You have no registered payment methods.")
            return
        
        # Retrieve the current overdue fee
        cur.execute("SELECT overdue_fee FROM public.client WHERE email = %s", (email,))
        result = cur.fetchone()
        
        overdue_fee = result[0]
        if overdue_fee == 0:
            print("You have no overdue fees to pay.")
            return
        
        print(f"Your current overdue fee is: ${overdue_fee:.2f}")
        
        # Ask for the payment amount
        amount = input("Enter the amount to pay or 'full' to pay the full amount: ")
        if amount.lower() == 'full':
            amount = overdue_fee
        else:
            try:
                amount = float(amount)
                if amount <= 0 or amount > overdue_fee:
                    print("Invalid amount. It must be positive and no more than the overdue fee.")
                    return
            except ValueError:
                print("Invalid input. Please enter a numerical value.")
                return

        # Display payment methods
        print("Available payment methods:")
        for idx, (card_number, company) in enumerate(payment_methods, 1):
            print(f"{idx}. Card Number: {card_number}, Company: {company}")

        # Choose a payment method
        choice = input("Choose a payment method or type 'cancel' to exit: ")
        if choice.lower() == 'cancel':
            print("Payment cancelled.")
            return
        
        try:
            choice_index = int(choice) - 1
            if choice_index < 0 or choice_index >= len(payment_methods):
                print("Invalid choice.")
                return
        except ValueError:
            print("Invalid input. Please enter a valid number.")
            return

        # Process the payment
        cur.execute("UPDATE public.client SET overdue_fee = overdue_fee - %s WHERE email = %s", (amount, email))
        conn.commit()
        print(f"Payment of ${amount:.2f} processed successfully. Thank you!")

    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        cur.close()
    
def insert_new_documents(conn):
    print("Inserting new document...")

    # Ask for the type of the document
    doc_type = input("Enter the type of the document (book, article, magazine): ").lower()
    if doc_type not in ['book', 'article', 'magazine']:
        print("Invalid document type.")
        return

    # Attributes based on type
    if doc_type == 'book':
        title = input("Enter the book title: ")
        isbn = input("Enter the ISBN: ")
        edition = input("Enter the book edition: ")
        pages = input("Enter the number of pages: ")
        year = input("Enter the year of publication: ")
    elif doc_type == 'article':
        title = input("Enter the article title: ")
        journal = input("Enter the journal name: ")
        number = input("Enter the article number: ")
        issue = input("Enter the journal issue: ")
        year = input("Enter the year of publication: ")
    elif doc_type == 'magazine':
        name = input("Enter the magazine name: ")
        isbn = input("Enter the ISBN: ")
        month = input("Enter the month of issue: ")
        year = input("Enter the year of publication: ")
    
    # Common attributes for all documents
    num_copies = input("Enter the number of copies (or 'digital' for unlimited digital copies): ").lower()
    if num_copies == 'digital':
        num_copies = 9999
    else:
        try:
            num_copies = int(num_copies)
            if num_copies < 1:
                raise ValueError
        except ValueError:
            print("Invalid number of copies. It must be a positive integer or 'digital'.")
            return
    publisher = input("Enter the publisher: ")

    cur = conn.cursor()
    try:
        # Insert document into the document table
        cur.execute("INSERT INTO public.document (type, num_copies, publisher) VALUES (%s, %s, %s) RETURNING id",
                    (doc_type, num_copies, publisher))
        doc_id = cur.fetchone()[0]

        # Insert into specific type table
        if doc_type == 'book':
            cur.execute("INSERT INTO public.book (id, title, isbn, edition, pages, year) VALUES (%s, %s, %s, %s, %s, %s)",
                        (doc_id, title, isbn, edition, pages, year))
        elif doc_type == 'article':
            cur.execute("INSERT INTO public.article (id, title, journal, number, issue, year) VALUES (%s, %s, %s, %s, %s, %s)",
                        (doc_id, title, journal, number, issue, year))
        elif doc_type == 'magazine':
            cur.execute("INSERT INTO public.magazine (id, name, isbn, month, year) VALUES (%s, %s, %s, %s, %s)",
                        (doc_id, name, isbn, month, year))

        # Handling authors
        while True:
            add_author = input("Do you want to add an author? (yes/no): ")
            if add_author.lower() != 'yes':
                break
            first_name = input("Enter the author's first name: ")
            last_name = input("Enter the author's last name: ")
            cur.execute("INSERT INTO public.written_by (id, first_name, last_name) VALUES (%s, %s, %s)",
                        (doc_id, first_name, last_name))

        conn.commit()
        print(f"Document and details added successfully with document ID {doc_id}.")
    except psycopg2.Error as e:
        print(f"An error occurred: {error}")
        conn.rollback()
    finally:
        cur.close()

def update_existing_documents(conn):
    print("Updating existing document...")

    doc_id = input("Enter the document ID you wish to edit: ")
    cur = conn.cursor()
    try:
        # Check if document exists and get type
        cur.execute("SELECT type FROM public.document WHERE id = %s", (doc_id,))
        result = cur.fetchone()
        if not result:
            print("No document found with that ID.")
            return
        doc_type = result[0]

        # Setup update options based on document type
        common_updates = {
            'publisher': "Update publisher",
            'num_copies': "Update number of copies"
        }
        type_specific_updates = {
            'book': {
                'title': "Update title",
                'isbn': "Update ISBN",
                'edition': "Update edition",
                'pages': "Update pages",
                'year': "Update publication year"
            },
            'article': {
                'title': "Update title",
                'journal': "Update journal",
                'number': "Update number",
                'issue': "Update issue",
                'year': "Update publication year"
            },
            'magazine': {
                'name': "Update name",
                'isbn': "Update ISBN",
                'month': "Update month",
                'year': "Update publication year"
            }
        }

        update_options = {**common_updates, **type_specific_updates[doc_type], 'authors': "Update authors"}
        option_list = list(update_options.items())
        option_list.append(('finish updating', "Finish Updating"))

        while True:
            print("\nWhat would you like to update?")
            for idx, (key, value) in enumerate(option_list, 1):
                print(f"{idx}. {value}")
            
            choice = input("Select an option: ")
            try:
                choice = int(choice)
                if not 1 <= choice <= len(option_list):
                    raise ValueError
            except ValueError:
                print("Invalid choice. Please try again.")
                continue

            if choice == len(option_list):
                break
            else:
                key, _ = option_list[choice - 1]
                
                if key == 'authors':
                    # Clear existing authors
                    cur.execute("DELETE FROM public.written_by WHERE id = %s", (doc_id,))
                    # Add new authors
                    while True:
                        add_author = input("Do you want to add an author? (yes/no): ")
                        if add_author.lower() != 'yes':
                            break
                        first_name = input("Enter the author's first name: ")
                        last_name = input("Enter the author's last name: ")
                        cur.execute("INSERT INTO public.written_by (id, first_name, last_name) VALUES (%s, %s, %s)", (doc_id, first_name, last_name))
                elif key == 'num_copies':
                    new_copies = input("Enter the new number of copies (or 'digital' for unlimited digital copies): ")
                    new_copies = 9999 if new_copies.lower() == 'digital' else int(new_copies)

                    # Validate against borrowed copies
                    cur.execute("SELECT COUNT(*) FROM public.borrows WHERE id = %s AND return_date IS NULL", (doc_id,))
                    num_borrowed = cur.fetchone()[0]
                    if new_copies < num_borrowed:
                        print(f"Cannot set the number of copies to {new_copies} as {num_borrowed} copies are currently borrowed.")
                    else:
                        cur.execute("UPDATE public.document SET num_copies = %s WHERE id = %s", (new_copies, doc_id))
                else:
                    new_value = input(f"Enter the new {update_options[key]}: ")
                    cur.execute(f"UPDATE public.{doc_type if key in type_specific_updates[doc_type] else 'document'} SET {key} = %s WHERE id = %s", (new_value, doc_id))

        conn.commit()
        print("Document updated successfully.")
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        cur.close()


def search_for_documents(conn):
    print("Welcome to the Document Search!")

    # Gather inputs
    doc_type = input("Enter the document type (book, magazine, article or any): ").lower().strip()
    title = input("Enter the title (or part of it): ")
    publisher = input("Enter publisher name (or part of it, leave empty if not searching by publisher): ")
    year = input("Enter the year of publication (leave empty if not searching by year): ")
    sort_by = input("Enter the attribute to sort by (title, year, copies): ")
    limit = input("Enter the maximum number of results to display: ")

    # Build the initial query based on document type
    query = "SELECT d.id, d.type, d.num_copies, d.publisher, b.title FROM public.document d "
    if doc_type in ['book', 'magazine', 'article']:
        query += f"INNER JOIN public.{doc_type} b ON d.id = b.id WHERE d.type = %s "
    else:
        query += "LEFT JOIN public.book b ON d.id = b.id WHERE True "

    params = [doc_type] if doc_type in ['book', 'magazine', 'article'] else []

    # Build conditions
    if title:
        query += "AND LOWER(b.title) LIKE LOWER(%s) "
        params.append(f"%{title}%")
    if publisher:
        query += "AND LOWER(d.publisher) LIKE LOWER(%s) "
        params.append(f"%{publisher}%")
    if year.isdigit():
        query += "AND b.year = %s "
        params.append(year)

    # Sorting and limiting results
    query += f"ORDER BY {sort_by} "
    if limit.isdigit():
        query += f"LIMIT {limit}"

    # Execute search
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        documents = cur.fetchall()
        print("Documents found:" if documents else "No documents found.")
        for doc in documents:
            print(f"ID: {doc[0]}, Type: {doc[1]}, Copies: {doc[2]}, Publisher: {doc[3]}, Title: {doc[4]}")
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
    finally:
        cur.close()

# #  muhammad implimentation seach document working code  
# def search_for_documents(conn):

#     print("Welcome to the Document Search!")

#     #input on document type
#     doc_type = input("Enter the document type (book, magazine, article or any): ").lower().strip()
    
#     #input for partial or full title of the document
#     title = input("Enter the title (or part of it): ")
    
#     # input for partial or full publisher name
#     publisher = input("Enter publisher name (or part of it, leave empty if not searching by publisher): ")
    
#     #input for the year of publication
#     year = input("Enter the year of publication (leave empty if not searching by year): ")

#     #construct the SQL query based on the specified document type
#     if doc_type in ['book', 'magazine', 'article']:
#         #query for specific document types with join on the document table
#         query = f"SELECT d.id, d.type, d.num_copies, d.publisher, b.title FROM public.document d INNER JOIN public.{doc_type} b ON d.id = b.id WHERE d.type = %s"
#         params = [doc_type]  # Initialize the parameters list with document type
#     else:
#         #if no specific type or 'any' is selected
#         query = "SELECT id, type, num_copies, publisher FROM public.document WHERE True"
#         params = []

#     #append condition to the sql for title search
#     if title:
#         query += " AND LOWER(b.title) LIKE LOWER(%s)"
#         params.append(f"%{title}%")
    
#     #append condition for publisher search if provided
#     if publisher:
#         query += " AND LOWER(d.publisher) LIKE LOWER(%s)"
#         params.append(f"%{publisher}%")
    
#     #append condition for filtering by year if it's provided and a valid number
#     if year.isdigit():
#         query += " AND b.year = %s"
#         params.append(year)


#     print("Executing search...")
#     cur = conn.cursor()
#     try:

#         cur.execute(query, params)
#         documents = cur.fetchall()  

#         #print the documents found or not found
#         if documents:
#             print("Documents found:")
#             for doc in documents:
#                 print(f"ID: {doc[0]}, Type: {doc[1]}, Copies: {doc[2]}, Publisher: {doc[3]}, Title: {doc[4]}")
#         else:
#             print("No documents found with the given criteria.")
#     except psycopg2.Error as e:
#         print(f"An error occurred while searching: {e}")
#         conn.rollback()  
#     finally:
#         cur.close()

# def search_for_documents(conn):
#     #print("Searching for documents...")
#     # Placeholder for functionality
    
    
    
#     print("for each possible search attribute (type,title,author(last name),publisher) enter a search term value, or else SKIP or START SEARCH")
#     print("supports string placeholders like % and _ BUT NOT YET!!")
#     print("for each search attribute specify EQUALS or CONTAINS the exact search term")
#     #print("for multiple search attributes specify AND or OR for multi-attribute searches")
    
#     type_search = input("enter type (book, magazine, article)")
    
#     #document name for mag, title for others
#     if type_search.lower()=='magazine':
#         query_string = 'SELECT name,last_name,first_name,publisher,num_copies FROM (SELECT * FROM written_by w,document d,'
#     else:
#         query_string = 'SELECT title,last_name,first_name,publisher,num_copies FROM (SELECT * FROM written_by w,document d,'
    
#     query_string+=type_search + ' t WHERE d.id = t.id AND w.id = d.id) AS a '
       
#     #query_string+=type_search + ' t WHERE d.id = t.id) AS a'
    
#     and_or = input("enter AND or OR if using multiple attribute search, else just hit enter")#or hit enter to start search
    
#     title_search = input("enter title search term, or SKIP")#or 'start search'
    
#     #for now don't want to search just all docs
#     #if (title_search == 'start search'):
#         #print("should start search now")
    
#     if title_search.lower()!='skip' and title_search.lower()!='':
#         title_match = input("enter EQUALS or CONTAINS the title search term")
        
#         query_string+='WHERE '
        
#         #document name for mag, title for others
#         if type_search.lower()=='magazine':
            
#             if title_match.lower()=='equals':
#                 query_string+='LOWER(name) = LOWER(' + '\'' + title_search.lower() + '\')'
#             if title_match.lower()=='contains':
#                 query_string+='LOWER(name) LIKE LOWER(' + '\'%' + title_search.lower() + '%\')'
                
#         else:
            
#             if title_match.lower()=='equals':
#                 query_string+='LOWER(title) = LOWER(' + '\'' + title_search.lower() + '\')'
#             if title_match.lower()=='contains':
#                 query_string+='LOWER(title) LIKE LOWER(' + '\'%' + title_search.lower() + '%\')'
    
    
#     #put this
#     #query_string+=" " + and_or + " "
        
        
    
#     author_search = input("enter author (last name) search term, SKIP or START SEARCH")
#     if (author_search.lower() == 'start search'):
#         print("should start search now1")
#         x=1
        
#         #query_string+=';'
#         #sort_attribute = input("Enter what attribute to sort on: title, last_name or publisher")
#         #sort_type = input("Enter what type of sort: ASC or DESC")
#         #num_returned = input("Enter how many records to return (e.g. 10,100) ")
        
#         #if sort_attribute.lower()=='title' and type_search.lower()=='magazine':
#         #    sort_attribute = 'name'
        
#         #query_string+= ' ORDER BY ' + sort_attribute.lower() + " " + sort_type.lower() + ' LIMIT ' + num_returned + ';'
    
    
    
#     elif author_search.lower()!='skip' and author_search.lower()!='':
        
#         if title_search.lower()=='skip':
#             query_string+='WHERE '
#         else:
#             query_string+=" " + and_or + " "
            
#         author_match = input("enter EQUALS or CONTAINS the author search term")
#         query_string+='LOWER('
        
#         if author_match.lower()=='equals':
#             query_string+='last_name) = LOWER(' + '\'' + author_search.lower() + '\')'
#         if author_match.lower()=='contains':
#             query_string+='last_name) LIKE LOWER(' + '\'%' + author_search.lower() + '%\')'
        
        
#     if (author_search.lower() == 'start search'):
#         publisher_search = 'start search'
#     else:
#         publisher_search = input("enter publisher search term, or START SEARCH")#don't need start search here
    
#     if (publisher_search.lower() == 'start search'):
#         print("should start search now2")
#         #query_string+=';'
#         sort_attribute = input("Enter what attribute to sort on: title, last_name or publisher")
#         sort_type = input("Enter what type of sort: ASC or DESC")
#         num_returned = input("Enter how many records to return (e.g. 10,100) ")
        
        
#         if sort_attribute.lower()=='title' and type_search.lower()=='magazine':
#             sort_attribute = 'name'
        
#         query_string+= ' ORDER BY ' + sort_attribute.lower() + " " + sort_type.lower() + ' LIMIT ' + num_returned + ';'
        
#     else:
#         query_string+=" " + and_or + " "
#         publisher_match = input("enter EQUALS or CONTAINS the publisher search term")
#         query_string+='LOWER('
        
#         if publisher_match.lower()=='equals':
#             query_string+='publisher) = LOWER(' + '\'' + publisher_search.lower() + '\')'
#         if publisher_match.lower()=='contains':
#             query_string+='publisher) LIKE LOWER(' + '\'%' + publisher_search.lower() + '%\')'
            
#         print("should start search now3")
#         #query_string+=';'
    
#         #print("query string is (before sort stuff):")
#         #print(query_string)
#         #should we add year?
    
#         sort_attribute = input("Enter what attribute to sort on: title, last_name or publisher")
#         sort_type = input("Enter what type of sort: ASC or DESC")
#         num_returned = input("Enter how many records to return (e.g. 10,100) ")
    
#         if sort_attribute.lower()=='title' and type_search.lower()=='magazine':
#             sort_attribute = 'name'
        
#         query_string+= ' ORDER BY ' + sort_attribute.lower() + " " + sort_type.lower() + ' LIMIT ' + num_returned + ';'
    
#     print("query string final:")
#     print(query_string)
#     print('need to print generic/bound header if possible, this is just for book')
#     print('document,last_name,first_name,publisher,num_copies')
    
    
#     cur = conn.cursor()
#     try:
#         cur.execute(query_string)#(query, params)
#         documents = cur.fetchall()
#         if documents:
#             print("Documents found:")
#             for doc in documents:
#                 print(doc)
#         else:
#             print("No documents found with the given criteria.")
#     except psycopg2.Error as e:
#         print(f"An error occurred while searching: {e}")
#         conn.rollback()
#     finally:
#         cur.close()
    
#     #still have to do the string placeholders (maybe not, user can add if they know it)
#     #show num copies or when next available
    
#     #delete this
#     #query_string = type_search + and_or + title_match + title_search + author_match + author_search + publisher_match + publisher_search + "sort on" + sort_attribute + sort_type + "limit to" + num_returned
#     #print("query string is:")
#     #print(query_string)

def librarian_menu(conn):
    while True:
        print("""
Librarian Menu:
1. Register new clients
2. Add new address
3. Add new payment method
4. Update client information
5. Delete clients
6. Insert new documents
7. Search for documents
8. Update existing documents
9. Exit
""")

        choice = input("Enter your choice: ")
        if choice == '1':
            register_new_client(conn)
        elif choice == '2':
            email = get_email(conn)
            if not email:
                print("No client found with that email.")
            else:
                add_new_address(conn, email)
        elif choice == '3':
            email = get_email(conn)
            if not email:
                print("No client found with that email.")
            else:
                add_payment_method(conn, email)
        elif choice == '4':
            email = get_email(conn)
            if not email:
                print("No client found with that email.")
            else:
                update_client_information(conn, email)
        elif choice == '5':
            delete_clients(conn)
        elif choice == '6':
            insert_new_documents(conn)
        elif choice == '7':
            search_for_documents(conn)
        elif choice == '8':
            update_existing_documents(conn)
        elif choice == '9':
            print("Signed out...")
            break
        else:
            print("Invalid choice. Please try again.")

def client_menu(conn, email):
    while True:
        print("""
Client Menu:
1. Update Information
2. Add New Address
3. Add New Payment Method
4. Search for Documents
5. Borrow Documents
6. Return Documents
7. Pay Overdue Fee
8. Exit
""")

        choice = input("Enter your choice: ")
        if choice == '1':
            update_client_information(conn, email)
        elif choice == '2':
            add_new_address(conn, email)
        elif choice == '3':
            add_new_payment_method(conn, email)
        elif choice == '4':
            search_for_documents(conn)
        elif choice == '5':
            borrow_documents(conn, email)
        elif choice == '6':
            return_documents(conn, email)
        elif choice == '7':
            pay_overdue_fee(conn, email)
        elif choice == '8':
            print("Signed out...")
            break
        else:
            print("Invalid choice. Please try again.")

# Main function to prompt for user input
def main():
    conn = connect()
    email = input("Enter your email: ")
    password = getpass("Enter your password: ")

    user_role = verify_credentials(email, password, conn)

    if user_role == "librarian":
        librarian_menu(conn)
    elif user_role == "client":
        client_menu(conn, email)

if __name__ == "__main__":
    main()





