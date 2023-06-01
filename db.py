import sqlite3


CREATE_TABLE_USERS = """
CREATE TABLE IF NOT EXISTS Users 
(
    username CHAR NOT NULL PRIMARY KEY,
    password CHAR NOT NULL
);
"""
CREATE_TABLE_FILES = """
CREATE TABLE IF NOT EXISTS Files 
(
    hash CHAR NOT NULL PRIMARY KEY,
    owner INT,
    FOREIGN KEY (owner) REFERENCES Users(username) 
);   
"""

INSERT_USER = "INSERT INTO Users(username, password) VALUES (?, ?);"
INSERT_FILE = "INSERT INTO Files(hash, owner) VALUES (?, ?);"

SELECT_USER = "SELECT * FROM Users WHERE username = ?;"
SELECT_USER_FILES = """
SELECT f.hash FROM Files f 
JOIN Users u ON f.owner = u.username
WHERE u.username = ?;
"""

DELETE_FILE = "DELETE FROM Files WHERE hash = ?"


class Cursor(sqlite3.Cursor):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
        self.connection.close()


class Database:
    def __init__(self, db_path):
        self.db_path = db_path

        self.create_tables()

    def _execute(self, sql, *args, commit=False, fetchone=True, fetchall=False):
        connection = sqlite3.connect(self.db_path)
        with connection.cursor(Cursor) as cursor:
            cursor.execute(sql, args)
            if commit:
                connection.commit()

            data = None
            if fetchone:
                data = cursor.fetchone()
            if fetchall:
                data = cursor.fetchall()

        return data

    def create_tables(self):
        self._execute(CREATE_TABLE_USERS, commit=True, fetchone=False)
        self._execute(CREATE_TABLE_FILES, commit=True, fetchone=False)

    def get_user(self, username):
        user = self._execute(SELECT_USER, username, commit=True, fetchone=True)

        return user

    def get_user_files(self, username):
        files = self._execute(SELECT_USER_FILES, username, commit=True, fetchone=False, fetchall=True)

        return files

    def add_user(self, username, password):
        self._execute(INSERT_USER, username, password, commit=True, fetchone=False)

    def add_file(self, file_hash, owner):
        self._execute(INSERT_FILE, file_hash, owner, commit=True, fetchone=False)

    def delete_file(self, file_hash):
        self._execute(DELETE_FILE, file_hash, commit=True, fetchone=False)
