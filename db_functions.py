import sqlite3
import itertools
import datetime


#! ДЛЯ РАБОТЫ С ПОЛЬЗОВАТЕЛЯМИ
def is_in_database(user_id):
    """Checks if user already in database."""

    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    users = cursor.execute(f'''SELECT COUNT(id) 
                            FROM users 
                            WHERE user_id=?
                            ''', (user_id,)).fetchall()[0][0]
    
    cursor.close()
    database.close()

    return users


def add_user(user_id, username):
    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    cursor.execute(f'''
        INSERT INTO users (user_id, username, products, receive, review, history_wb, history_ozon)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, username, '[]', '[]', '[]', '[]', '[]',))
    
    database.commit()
    cursor.close()
    database.close()


def drop_settings(user_id):
    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    cursor.execute(f'''UPDATE users
                    SET input=?, input_data=?, products=?, receive=?, review=?, smiles=?, marketplace=?
                    WHERE user_id=?
                    ''', (False, None, '[]', '[]', '[]', None, None, user_id,))

    database.commit()
    cursor.close()
    database.close()


def get_users_field_info(user_id, field):
    database = sqlite3.connect("db.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    cursor = database.cursor()

    info = cursor.execute(f'''SELECT {field}
                            FROM users 
                            WHERE user_id=?
                            ''', (user_id,)).fetchall()[0][0]
    
    cursor.close()
    database.close

    return info


def update_users_field(user_id, field, value):
    database = sqlite3.connect("db.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    cursor = database.cursor()

    cursor.execute(f'''UPDATE users
                    SET {field}=?
                    WHERE user_id=?
                    ''', (value, user_id,))

    database.commit()
    cursor.close()
    database.close()


def select_user_info(user_id):
    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    info = cursor.execute(f'''SELECT *
                            FROM users 
                            WHERE user_id=?
                            ''', (user_id,)).fetchall()[0]
    
    cursor.close()
    database.close()

    return info


def select_again_eligible_users(products, marketplace):
    database = sqlite3.connect("db.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    cursor = database.cursor()

    time_filter = datetime.datetime.utcnow() - datetime.timedelta(days=7)

    request = ''

    for product in products:
        request += f'''history_{marketplace} NOT LIKE "%'{product[1]}'%" OR '''
    
    request = '(' + request.rstrip(' OR ') + ')'

    ids = cursor.execute(f'''SELECT user_id 
                            FROM users 
                            WHERE products=? AND receive=? AND review=? AND marketplace IS ? AND
                            eligible_{marketplace}=? AND smiles IS ? AND last_participate_{marketplace}<? AND
                            {request}
                            ''', ('[]', '[]', '[]', None, False, None, time_filter,)).fetchall()
                            
    cursor.close()
    database.close()

    if ids:
        ids = list(itertools.chain.from_iterable(ids))

    return ids


#! ДЛЯ РАБОТЫ С ТОВАРАМИ
def is_product_in_database(product, marketplace):
    """Checks if user already in database."""

    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    users = cursor.execute(f'''SELECT COUNT(id) 
                            FROM products
                            WHERE product=? AND marketplace=?
                            ''', (product, marketplace)).fetchall()[0][0]
    
    cursor.close()
    database.close()

    return users


def drop_active_products():
    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    cursor.execute('UPDATE products SET active=?', (False,))
        
    database.commit()
    cursor.close()
    database.close()


def activate_product(product, counter, marketplace):
    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    try:
        counter = int(counter)
    except:
        counter = None

    status = True
    if counter == 0:
        status = False

    cursor.execute('''UPDATE products 
                    SET active=?, counter=?
                    WHERE product=? AND marketplace=?
                    ''', (status, counter, product, marketplace,))
        
    database.commit()
    cursor.close()
    database.close()


def add_product(product, marketplace):
    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    counter = None
    try:
        counter = int(product[2])
    except:
        pass

    cursor.execute(f'''
        INSERT INTO products (product, photo, counter, marketplace)
        VALUES (?, ?, ?, ?)
        ''', (product[0], product[1], counter, marketplace,))
        
    database.commit()
    cursor.close()
    database.close()


def select_active_products(marketplace):
    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    products = cursor.execute(f'''SELECT id, product 
                            FROM products
                            WHERE active=? AND marketplace=?
                            ORDER BY id
                            ''', (True, marketplace,)).fetchall()
    
    cursor.close()
    database.close()

    return products


def select_products_photos(product, marketplace):
    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    photo = cursor.execute(f'''SELECT photo
                            FROM products
                            WHERE product=? AND marketplace=?
                            ''', (product, marketplace,)).fetchall()[0][0]
    
    cursor.close()
    database.close()

    return photo


def select_products_id(product, marketplace):
    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    product_id = cursor.execute(f'''SELECT id
                            FROM products
                            WHERE product=? AND marketplace=?
                            ''', (product, marketplace,)).fetchall()[0][0]
    
    cursor.close()
    database.close()

    return product_id


def get_products_field_info(product_id, field):
    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    info = cursor.execute(f'''SELECT {field}
                            FROM products
                            WHERE id=?
                            ''', (product_id,)).fetchall()[0][0]
    
    cursor.close()
    database.close

    return info


def update_product_field(product_id, field, value):
    database = sqlite3.connect("db.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    cursor = database.cursor()

    cursor.execute(f'''UPDATE products
                    SET {field}=?
                    WHERE id=?
                    ''', (value, product_id,))

    database.commit()
    cursor.close()
    database.close()


#! ДЛЯ РАБОТЫ С ТЕКСТОМ
def update_text(name, text):
    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    cursor.execute(f'''UPDATE texts
                    SET text=?
                    WHERE name=?
                    ''', (text, name,))

    database.commit()
    cursor.close()
    database.close()


def get_text(name):
    database = sqlite3.connect("db.db")
    cursor = database.cursor()

    text = cursor.execute(f'''SELECT text
                            FROM texts
                            WHERE name=?
                            ''', (name,)).fetchall()[0][0]
    
    cursor.close()
    database.close

    return text
