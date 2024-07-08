import os
import sqlite3
from peewee import SqliteDatabase
from manage import address


#
# class Table:
#     def __init__(self, table_name):
#         self.table_name = table_name
#         self.columns = list()
#
#     # def add_column(self, *args, **kwargs):
#     #     if len(self.columns) == 0:
#     #         column = self.
#     #         self.columns.append(column)
#
#     class Column:
#         def __init__(self, name, default=None, nullable=True, unique=False, primary_key=False, auto_fill=False):
#             self.name = name
#             self.nullable = nullable
#             self.unique = unique
#             self.default = default
#             self.primary_key = primary_key
#             self.auto_fill = auto_fill
#             self.column_type = None
#
#     class INTEGER(Column):
#         def __init__(self, *args, **kwargs):
#             super().__init__(*args, **kwargs)
#             self.column_type = 'INTEGER'
#
#     class TEXT(Column):
#         def __init__(self, max_length, *args, **kwargs):
#             super().__init__(*args, **kwargs)
#             self.max_length = max_length
#             self.column_type = 'TEXT'
#
#     class STRING(Column):
#         def __init__(self, *args, **kwargs):
#             super().__init__(*args, **kwargs)
#             self.column_type = 'TEXT'
#
#     class DATETIME(Column):
#         def __init__(self, auto_add_now=False, *args, **kwargs):
#             super().__init__(*args, **kwargs)
#             self.auto_add_now = auto_add_now
#             self.column_type = 'DATETIME'
#
#     class BOOLEAN(Column):
#         def __init__(self, *args, **kwargs):
#             super().__init__(*args, **kwargs)
#             self.column_type = 'BOOLEAN'
#
#
# t = Table('users')
# t.columns = [
#     t.INTEGER(name='id', primary_key=True, auto_fill=True, nullable=False, unique=True),
#     t.INTEGER(name='uid', unique=True, nullable=False),
#     t.STRING(name='user_name'),
#     t.INTEGER(name='coin', default=0),
#     t.TEXT(name='wallet_address', max_length=300),
#     t.DATETIME(name='created', auto_add_now=True),
#     t.DATETIME(name='last_bonus', nullable=True),
#     t.INTEGER(name='bonus_count', default=0),
#     t.INTEGER(name='referral_user', default=0),
#     t.INTEGER(name='agent', nullable=False),
#     t.BOOLEAN(name='request_withdrawal', default=False),
#     t.INTEGER(name='transaction_amount', default=0)
# ]

class DB:
    def __init__(self, db_name):
        # Check if the database file exists
        self.tables = list()
        self.db_path = address.db + '\\' + db_name + '.db'
        self.create_db_file()
        self.db = SqliteDatabase(self.db_path)

    def migrate(self):
        self.db.connect()
        self.create_db_tables()
        # self.db.evolve()
        self.db.close()

    def add_to_table_list(self, tables):
        if tables is list:
            for _ in tables:
                self.tables.append(_)
        else:
            self.tables.append(tables)

    def create_db_tables(self):
        self.db.connect(reuse_if_open=True)
        self.db.create_tables(self.tables)
        self.db.close()

    def create_db_file(self):
        if not os.path.isfile(self.db_path):
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('CREATE TABLE IF NOT EXISTS creation (id INTEGER PRIMARY KEY, created DATETIME DEFAULT CURRENT_TIMESTAMP);')
                conn.commit()
                cursor.execute('DROP TABLE IF EXISTS creation;')
                conn.commit()
                conn.close()
            except BaseException as e:
                print(f'Error creating database file: {self.db_path}')


    def add_table(self, table):
        self.db.connect()
        if table is list():
            self.db.create_tables(table)
            for _ in table:
                self.tables.append(_)
        else:
            self.db.create_tables([table])
            self.tables.append(table)
        self.db.close()

    def drop_table(self, table):
        self.db.connect()
        if table is list():
            self.db.drop_tables(table, safe=True)
            for _ in table:
                self.tables.remove(_)
        else:
            self.db.create_tables([table], safe=True)
            self.tables.remove(table)
        self.db.close()

    def sql_insert_query(self, query):
        try:
            self.db.connect()
            self.db.execute(query=query, commit=True)
            self.db.close()
        except BaseException as e:
            self.db.rollback()
            self.db.close()
            return False

        return True

    def read(self, uid):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Selecting data from the 'users' table
            cursor.execute("SELECT * FROM users WHERE uid=?", (uid, ))
        except sqlite3.OperationalError:
            conn.close()
            return None

        # Fetching all results
        rows = cursor.fetchall()

        data = dict()

        # Iterating through the rows
        for row in rows:
            data['id'] = row[0]
            data['uid'] = row[1]
            data['user_name'] = row[2]
            data['coin'] = row[3]
            data['wallet_address'] = row[4]
            data['created'] = row[5]
            data['last_bonus'] = row[6]
            data['bonus_count'] = row[7]
            data['referral_user'] = row[8]
            data['agent'] = row[9]
            data['request_withdrawal'] = row[10]
            data['transaction_amount'] = row[11]

        conn.close()

        if data:
            return data
        else:
            return None
            # data['id'] = None
            # data['uid'] = None
            # data['user_name'] = None
            # data['coin'] = None
            # data['wallet_address'] = None
            # data['created'] = None
            # data['last_bonus'] = None
            # data['bonus_count'] = None
            # data['referral_user'] = None
            # data['agent'] = None
            # data['request_withdrawal'] = None
            # data['transaction_amount'] = None

    def all(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Selecting data from the 'users' table
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()
            cursor.close()
        except sqlite3.OperationalError:
            conn.close()
            return None

        data = list()

        # Iterating through the rows
        for row in rows:
            user = dict()
            user['id'] = row[0]
            user['uid'] = row[1]
            user['user_name'] = row[2]
            user['coin'] = row[3]
            user['wallet_address'] = row[4]
            user['created'] = row[5]
            user['last_bonus'] = row[6]
            user['bonus_count'] = row[7]
            user['referral_user'] = row[8]
            user['agent'] = row[9]
            user['request_withdrawal'] = row[10]
            user['transaction_amount'] = row[11]
            # add user to data dict
            data.append(user)

        if data:
            return data
        else:
            return []



    def get_user_attr(self, uid, attr):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        attributes = [
            'id',
            'uid',
            'user_name',
            'coin',
            'wallet_address',
            'created',
            'last_bonus',
            'bonus_count',
            'referral_user',
            'agent',
            'request_withdrawal',
            'transaction_amount'
        ]
        attr_name = None
        if attr in attributes:
            attr_name = attr
        try:
            cursor.execute('''SELECT {} FROM users WHERE uid=?'''.format(attr_name), (uid, ))
        except sqlite3.OperationalError:
            conn.close()
            return None
        result = cursor.fetchall()
        conn.close()
        if result:
            return result[0][0]
        else:
            return None

    def update_user_attr(self, uid, attr, value):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        attributes = [
            'id',
            'uid',
            'user_name',
            'coin',
            'wallet_address',
            'created',
            'last_bonus',
            'bonus_count',
            'referral_user',
            'agent',
            'request_withdrawal',
            'transaction_amount'
        ]
        attr_name = None
        if attr in attributes:
            attr_name = attr
        try:
            cursor.execute('''UPDATE users SET {}=? WHERE uid=?'''.format(attr_name), (value, uid))
        except sqlite3.IntegrityError:
            conn.close()
            print(f'error setting {attr} of user {uid} with value {value}!')
        conn.commit()
        conn.close()

    def is_user_exist(self, uid):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        user = None
        try:
            cursor.execute('''SELECT * FROM users WHERE uid=?''', (uid,))
            user = cursor.fetchall()
            conn.close()
        except sqlite3.OperationalError:
            conn.close()
        if user is not None:
            try:
                if user[0][1] == uid:
                    return True
                else:
                    return False
            except IndexError:
                return False
        else:
            return False

    def get_count(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Inserting data into the 'users' table
            cursor.execute("SELECT COUNT(*) FROM users;")
            data = cursor.fetchall()
            conn.close()
        except sqlite3.OperationalError:
            data = None
            conn.close()
            print(f'error during calculate count: TABLE users!')

        if data is not None:
            return data[0][0]
        else:
            return None

    def first_and_last(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''SELECT * FROM users
                ORDER BY created ASC
                LIMIT 1;
            ''')
            oldest = cursor.fetchone()
            cursor.execute('''SELECT * FROM users
                ORDER BY created DESC
                LIMIT 1;
            ''')
            newest = cursor.fetchone()
            conn.close()
        except sqlite3.OperationalError:
            oldest = None
            newest = None
            conn.close()

        oldest_uid = None
        newest_uid = None
        oldest_data = None
        newest_data = None

        print(f'oldest: {oldest}')
        print(f'newest: {newest}')

        if oldest[0] and newest[0]:
            oldest_uid = oldest[1]
            newest_uid = newest[1]
            oldest_data = self.read(oldest_uid)
            newest_data = self.read(newest_uid)

        if oldest_data and newest_data:
            return {'success': True, 'oldest': oldest_data, 'newest': newest_data}
        else:
            return {'success': False, 'oldest': None, 'newest': None}

    def search_by_setting(self, attr, minimum, count, attr_is_bool=False, sameness=False):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            if attr_is_bool is True or sameness is True:
                cursor.execute("SELECT * FROM users WHERE {} = ?;".format(attr), (minimum, ))
                rows = cursor.fetchall()
                cursor.execute("SELECT COUNT(*) FROM users WHERE {} = ?;".format(attr), (minimum, ))
                rows_count = cursor.fetchall()
            else:
                cursor.execute("SELECT * FROM users WHERE {} >= ?;".format(attr), (minimum,))
                rows = cursor.fetchall()
                cursor.execute("SELECT COUNT(*) FROM users WHERE {} >= ?;".format(attr), (minimum,))
                rows_count = cursor.fetchall()
            conn.close()
        except sqlite3.OperationalError:
            rows = None
            rows_count = None
            conn.close()

        user_count = 1
        users = list()

        if rows:
            for row in rows:
                if user_count <= count:
                    user_count += 1
                    data = self.read(row[1])
                    users.append(data)
                else:
                    break

        if rows_count and users:
            return {'count': rows_count[0][0], 'users': users}
        else:
            return {'count': 0, 'users': []}

    def create_user(self, uid, user_name):
        conn = sqlite3.connect(self.db_path)

        # Assuming 'conn' is your database connection object
        cursor = conn.cursor()

        try:
            # Inserting data into the 'users' table
            cursor.execute("INSERT INTO users (uid, user_name) VALUES (?, ?)", (uid, user_name))
        except sqlite3.OperationalError:
            conn.close()
            print(f'error creating user with uid=[{uid}] and user_name=[{user_name}]!')

        # Committing the changes
        conn.commit()

        conn.close()


if __name__ == '__main__':
    db = DB('telebot')

