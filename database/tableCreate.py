import sqlite3

try:
    sqliteConnection = sqlite3.connect('chat.db')
    sqlite_create_table_query = '''CREATE TABLE chatHistory_en (
                                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                                prompt TEXT NOT NULL,
                                response TEXT,
                                source1 TEXT,
                                source2 TEXT,
                                flagA INTEGER DEFAULT 0,
                                flagB INTEGER DEFAULT 0,
                                chatID INTEGER NOT NULL,
                                startTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                duration TIMESTAMP);'''

    cursor = sqliteConnection.cursor()
    print("Successfully Connected to SQLite")
    cursor.execute(sqlite_create_table_query)
    sqliteConnection.commit()
    print("SQLite table created")

    cursor.close()

except sqlite3.Error as error:
    print("Error while creating a sqlite table", error)
finally:
    if sqliteConnection:
        sqliteConnection.close()
        print("sqlite connection is closed")
