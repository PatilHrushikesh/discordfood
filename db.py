import sqlite3
from typing import List, Tuple, Any

class Database:
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            print(f"Connected to {self.db_name} successfully.")
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")

    def disconnect(self):
        if self.conn:
            self.conn.close()
            print("Database connection closed.")

    def execute_query(self, query: str, params: Tuple[Any, ...] = None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.conn.commit()
            print("Query executed successfully.")
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")

    def fetch_all(self, query: str, params: Tuple[Any, ...] = None) -> List[Tuple[Any, ...]]:
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching data: {e}")
            return []

    def create_table(self, table_name: str, columns: List[str]):
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
        self.execute_query(query)

    def insert_data(self, table_name: str, data: Tuple[Any, ...]):
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table_name} VALUES ({placeholders})"
        self.execute_query(query, data)

    def update_data(self, table_name: str, set_values: str, condition: str):
        query = f"UPDATE {table_name} SET {set_values} WHERE {condition}"
        self.execute_query(query)

    def delete_data(self, table_name: str, condition: str):
        query = f"DELETE FROM {table_name} WHERE {condition}"
        self.execute_query(query)

# Example usage:
if __name__ == "__main__":
    db = Database("example.db")
    db.connect()

    # Create a table
    db.create_table("users", ["id INTEGER PRIMARY KEY", "name TEXT", "age INTEGER"])

    # Insert data
    db.insert_data("users", (1, "Alice", 30))
    db.insert_data("users", (2, "Bob", 25))

    # Update data
    db.update_data("users", "age = 31", "name = 'Alice'")

    # Fetch and print all data
    results = db.fetch_all("SELECT * FROM users")
    for row in results:
        print(row)

    # Delete data
    db.delete_data("users", "name = 'Bob'")

    # Fetch and print all data again
    results = db.fetch_all("SELECT * FROM users")
    for row in results:
        print(row)

    db.disconnect()