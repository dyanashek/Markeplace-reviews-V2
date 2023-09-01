import telebot
import time

import db_functions
import keyboards
import text
import config


bot = telebot.TeleBot(config.TELEGRAM_TOKEN)


def get_texts_from_google():
    texts = config.WORK_SHEET.col_values(1)[1::]

    return texts


def get_wb_products_from_google():
    products = config.WORK_SHEET.col_values(2)[1::]
    photos = config.WORK_SHEET.col_values(3)[1::]
    counter = config.WORK_SHEET.col_values(4)[1::]

    return list(zip(products, photos, counter))


def get_ozon_products_from_google():
    products = config.WORK_SHEET.col_values(5)[1::]
    photos = config.WORK_SHEET.col_values(6)[1::]
    counter = config.WORK_SHEET.col_values(7)[1::]

    return list(zip(products, photos, counter))


def update_database(user_id):
    wb_products = get_wb_products_from_google()
    ozon_products = get_ozon_products_from_google()
    db_functions.drop_active_products()

    for wb_product in wb_products:
        if not db_functions.is_product_in_database(wb_product[0], 'wb'):
            db_functions.add_product(wb_product, 'wb')
        else:
            db_functions.activate_product(wb_product[0], wb_product[2], 'wb')
    
    for ozon_product in ozon_products:
        if not db_functions.is_product_in_database(ozon_product[0], 'ozon'):
            db_functions.add_product(ozon_product, 'ozon')
        else:
            db_functions.activate_product(ozon_product[0], ozon_product[2], 'ozon')
    
    texts = get_texts_from_google()
    db_functions.update_text('start', texts[0])
    db_functions.update_text('sorry', texts[1])
    db_functions.update_text('rules', texts[2])
    db_functions.update_text('products', texts[3])

    try:
        bot.send_message(chat_id=user_id,
                         text=text.UPDATED,
                         parse_mode='Markdown',
                         )
    except:
        pass


def inform_manager_bought(user_id):
    user_info = db_functions.select_user_info(user_id)

    username = user_info[2]

    products = eval(user_info[10])
    smiles = user_info[13]

    receive = eval(user_info[11])

    marketplace = db_functions.get_users_field_info(user_id, 'marketplace')
    
    reply_text = text.inform_manager_bought(username, products, smiles, marketplace)

    try:
        sended_message = bot.send_message(chat_id=config.MANAGER_ID,
                        text=reply_text,
                        parse_mode='Markdown',
                        )
    except:
        pass

    group_media = []
    for photo in receive:
        group_media.append(telebot.types.InputMediaPhoto(photo))

    try:
        bot.send_media_group(chat_id=config.MANAGER_ID,
                                media=group_media,
                                reply_to_message_id=sended_message.id,
                                timeout=30,
                                )
    except:
        pass


def inform_manager(user_id):
    user_info = db_functions.select_user_info(user_id)

    username = user_info[2]

    payment_method = user_info[3]
    bank = user_info[4]
    account = user_info[5]

    products = eval(user_info[10])
    smiles = user_info[13]

    receive = eval(user_info[11])
    reviews = eval(user_info[12])

    marketplace = db_functions.get_users_field_info(user_id, 'marketplace')
    
    reply_text = text.inform_manager(username, payment_method, bank, account, products, smiles, marketplace)

    try:
        sended_message = bot.send_message(chat_id=config.MANAGER_ID,
                        text=reply_text,
                        parse_mode='Markdown',
                        )
    except:
        pass

    group_media = []
    for photo in receive:
        group_media.append(telebot.types.InputMediaPhoto(photo))

    try:
        bot.send_media_group(chat_id=config.MANAGER_ID,
                                media=group_media,
                                reply_to_message_id=sended_message.id,
                                timeout=30,
                                )
    except:
        pass
    
    group_media = []
    for photo in reviews:
        group_media.append(telebot.types.InputMediaPhoto(photo))

    try:
        bot.send_media_group(chat_id=config.MANAGER_ID,
                                media=group_media,
                                reply_to_message_id=sended_message.id,
                                timeout=30,
                                )
    except:
        pass

    db_functions.drop_settings(user_id)


def update_eligible():
    while True:
        products_wb = db_functions.select_active_products('wb')
        products_ozon = db_functions.select_active_products('ozon')

        users_ids_wb = []
        if products_wb:
            while len(products_wb) < 3:
                products_wb.append(products_wb[0])

            users_ids_wb = db_functions.select_again_eligible_users(products_wb, 'wb')
        
        users_ids_ozon = []
        if products_ozon:
            while len(products_ozon) < 3:
                products_ozon.append(products_ozon[0])

            users_ids_ozon = db_functions.select_again_eligible_users(products_ozon, 'ozon')

        users_ids = list(set(users_ids_wb + users_ids_ozon))

        if users_ids:
            for wb_user in users_ids_wb:
                db_functions.update_users_field(wb_user, 'eligible_wb', True)
            
            for ozon_user in users_ids_ozon:
                db_functions.update_users_field(ozon_user, 'eligible_ozon', True)

            for user_id in users_ids:
                try:
                    bot.send_message(chat_id=user_id,
                                    text=text.NEW_PROMO,
                                    reply_markup=keyboards.action_keyboard(),
                                    parse_mode='Markdown',
                                    disable_notification=False,
                                    )
                except:
                    pass
                
            time.sleep(86400)