import sqlite3
import logging

database = sqlite3.connect("db.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
cursor = database.cursor()

try:
    cursor.execute('''CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        username TEXT,
        payment_form TEXT,
        bank TEXT,
        account TEXT,
        input BOOLEAN DEFAULT False,
        input_data TEXT,
        history_wb TEXT,
        history_ozon TEXT,
        products TEXT,
        receive TEXT,
        review TEXT,
        smiles TEXT,
        eligible_wb BOOLEAN DEFAULT True,
        eligible_ozon BOOLEAN DEFAULT True,
        last_participate_wb TIMESTAMP,
        last_participate_ozon TIMESTAMP,
        marketplace
    )''')
except Exception as ex:
    logging.error(f'Users table already exists. {ex}')

try:
    cursor.execute('''CREATE TABLE texts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        text TEXT
    )''')
except Exception as ex:
    logging.error(f'Text table already exists. {ex}')

try:
    cursor.execute('''CREATE TABLE products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product TEXT,
        photo TEXT,
        active BOOLEAN DEFAULT True,
        counter INTEGER,
        marketplace TEXT
    )''')
except Exception as ex:
    logging.error(f'Products table already exists. {ex}')

# cursor.execute("DELETE FROM referrals WHERE id<>1000")
# database.commit()