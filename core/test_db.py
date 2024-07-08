import sqlite3


def get_column_info(database_file, table_name):
    # Connect to the SQLite database
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()

    # Query the SQLite system table for column information
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns_info = cursor.fetchall()

    # Close the database connection
    conn.close()

    return columns_info


if __name__ == '__main__':
    # Example usage
    db_file = '../db/shiba-inu.db'
    tb_name = 'users'
    _info = get_column_info(db_file, tb_name)

    print(_info)

    print('*' * 50)

    # Print column information
    for column in _info:
        print(column)

