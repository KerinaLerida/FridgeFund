import sqlite3

class SimpleSQLiteDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        create_users_table_query = '''
            CREATE TABLE IF NOT EXISTS users (
                id BIGINT PRIMARY KEY NOT NULL,
                name VARCHAR(100) NOT NULL,
                balance DOUBLE UNSIGNED
            )
        '''
        create_items_table_query = '''
            CREATE TABLE IF NOT EXISTS items (
                id INT PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                quantity INT UNSIGNED,
                price DOUBLE UNSIGNED NOT NULL
            )
        '''
        with self.connection:
            self.connection.execute(create_users_table_query)
            self.connection.execute(create_items_table_query)

    # Users Table
    def insert_user(self, id_user, name, balance):
        insert_query = '''
            INSERT INTO users (id, name, balance) VALUES (?,?,?)
        '''
        with self.connection:
            self.connection.execute(insert_query, (id_user, name, balance))

    def update_balance_by_id(self, id_user, new_balance):
        update_query = '''
            UPDATE users
            SET balance = ?
            WHERE id = ?
        '''
        with self.connection:
            self.connection.execute(update_query, (new_balance, id_user))

    def get_user_by_id(self, id_user):
        select_query = '''
            SELECT id, name, balance
            FROM users
            WHERE id = ?
        '''
        with self.connection:
            cursor = self.connection.execute(select_query, (id_user,))
            return cursor.fetchone()

    def get_all_users(self):
        select_all_query = '''
            SELECT id, name, balance
            FROM users
        '''
        with self.connection:
            cursor = self.connection.execute(select_all_query)
            return cursor.fetchall()

    # Items Table
    def insert_item(self, name_item, quantity_item, price_item):
        insert_query = '''
            INSERT INTO items (name,quantity,price) VALUES (?,?,?)
        '''
        with self.connection:
            self.connection.execute(insert_query, (name_item, quantity_item, price_item))

    def update_quantity_by_name(self, name_item, new_quantity):
        update_query = '''
            UPDATE items
            SET quantity = new_quantity
            WHERE name = name_item
        '''
        with self.connection:
            self.connection.execute(update_query, (new_quantity, name_item))

    def update_price_by_name(self, new_price, name_item):
        update_query = '''
            UPDATE items
            SET price = ?
            WHERE name = ?
        '''
        with self.connection:
            self.connection.execute(update_query, (new_price, name_item))

    def get_item_by_name(self, name_item):
        select_query = '''
            SELECT id, name, quantity, price
            FROM items
            WHERE name = ?
        '''
        with self.connection:
            cursor = self.connection.execute(select_query, (name_item,))
            return cursor.fetchone()

    def get_all_items(self):
        select_all_query = '''
            SELECT id, name, quantity, price
            FROM items
        '''
        with self.connection:
            cursor = self.connection.execute(select_all_query)
            return cursor.fetchall()

    def close_connection(self):
        self.connection.close()
"""
# Example usage
database = SimpleSQLiteDatabase('my_database.db')

# Insert a new user
database.insert_user('John Doe', 1000)

# Insert a new item
database.insert_item('Apple', 5, 100)

# Update user balance by name
database.update_balance_by_name('John Doe', 1200)

# Update item stock by name
database.update_stock_by_name('Apple', 95)

# Get user by name
user = database.get_user_by_name('John Doe')
print(user)

# Get item by name
item = database.get_item_by_name('Apple')
print(item)

# Get all users
all_users = database.get_all_users()
print(all_users)

# Get all items
all_items = database.get_all_items()
print(all_items)

# Don't forget to close the connection when you're done
database.close_connection()
"""
