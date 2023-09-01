from telebot import types

import config
import db_functions


def action_keyboard():
    """Generates main keyboard that have option of filling form, check instagram."""

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Хочу!', callback_data = 'yes'))
    keyboard.add(types.InlineKeyboardButton('Нет', callback_data = 'no'))

    return keyboard


def ready_keyboard():
    """Generates main keyboard that have option of filling form, check instagram."""

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Готов(-а) заказать!', callback_data = 'ready'))

    return keyboard


def username_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Принять участие!', callback_data = 'username'))

    return keyboard


def products_keyboard(user_id, products_for_select, products, marketplace):
    keyboard = types.InlineKeyboardMarkup()
    users_products = eval(db_functions.get_users_field_info(user_id, 'products'))

    for num, product in enumerate(products_for_select):
        other_products = list(dict(products).keys())
        other_products.remove(product[0])
        
        if product[1] in users_products:
            keyboard.add(types.InlineKeyboardButton(f'✅ {num + 1}. {product[1]}', callback_data = f'product_1_{product[0]}_{other_products[0]}_{other_products[1]}_{marketplace}'))
        else:
            keyboard.add(types.InlineKeyboardButton(f'{num + 1}. {product[1]}', callback_data = f'product_0_{product[0]}_{other_products[0]}_{other_products[1]}_{marketplace}'))
    
    other_products = list(dict(products).keys())
    keyboard.add(types.InlineKeyboardButton('Готово!', callback_data = f'done_{other_products[0]}_{other_products[1]}_{other_products[2]}_{marketplace}'))

    return keyboard


def received_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Получено!', callback_data = 'received'))

    return keyboard


def payment_method_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('СБП (по номеру телефона)', callback_data = 'method_sbp'))
    keyboard.add(types.InlineKeyboardButton('По номеру карты', callback_data = 'method_card'))

    return keyboard


def banks_keyboard():
    keyboard = types.InlineKeyboardMarkup()

    sber = types.InlineKeyboardButton('Сбер', callback_data = 'bank_sber')
    tinkoff = types.InlineKeyboardButton('Тинькофф', callback_data = 'bank_tinkoff')
    vtb = types.InlineKeyboardButton('ВТБ', callback_data = 'bank_vtb')
    open = types.InlineKeyboardButton('Открытие', callback_data = 'bank_open')
    
    keyboard.add(sber, tinkoff)
    keyboard.add(vtb, open)

    keyboard.add(types.InlineKeyboardButton('Альфа-Банк', callback_data = 'bank_alfa'))
    keyboard.add(types.InlineKeyboardButton('Райффайзен Банк', callback_data = 'bank_raif'))

    keyboard.add(types.InlineKeyboardButton('⬅️ Назад', callback_data = 'back_method'))
    
    return keyboard


def confirm_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('✅ Подтвердить', callback_data = 'confirm'))
    keyboard.add(types.InlineKeyboardButton('🔁 Ввести заново', callback_data = 'reenter'))

    return keyboard


def update_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('🔄 Позвать администратора', callback_data = 'update'))

    return keyboard


def help_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Да', callback_data = 'help_yes'), types.InlineKeyboardButton('Нет', callback_data = 'help_no'))

    return keyboard

def marketplace_keyboard(wb, ozon):
    keyboard = types.InlineKeyboardMarkup()
    if wb:
        keyboard.add(types.InlineKeyboardButton('🛒 Wildberries', callback_data = 'marketplace_wb'))
    if ozon:
        keyboard.add(types.InlineKeyboardButton('🛍 Ozon', callback_data = 'marketplace_ozon'))

    return keyboard