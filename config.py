import os
import gspread
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

MANAGER_ID = os.getenv('MANAGER_ID')

SPREAD_NAME = os.getenv('SPREAD_NAME')
LIST_NAME = os.getenv('LIST_NAME')

SERVICE_ACC = gspread.service_account(filename='service_account.json')
SHEET = SERVICE_ACC.open(SPREAD_NAME)
WORK_SHEET = SHEET.worksheet(LIST_NAME)

MAX_PRODUCTS = 3

SMILES = ['😂', '🙏', '😘', '😍', '😊', '😁', '😄', '💋', '😳', '😉',\
        '😚', '😋', '😅', '😇', '😜', '🤪', '🤭', '🤗', '😏', '😈', '🥺', '😱', '😌']

BANKS = {
    'sber' : 'Сбер',
    'tinkoff' : 'Тинькофф',
    'vtb' : 'ВТБ',
    'open' : 'Открытие',
    'alfa' : 'Альфа-Банк',
    'raif' : 'Райффайзен Банк',
}

PAYMENT_METHODS = {
    'sbp' : 'СБП (по номеру телефона):',
    'card' : 'По номеру карты:'
}