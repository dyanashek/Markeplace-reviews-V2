import re


def escape_markdown(text):
    characters_to_escape = ['_', '*', '[', ']', '`']
    for char in characters_to_escape:
        text = text.replace(char, '\\' + char)

    return text


def validate_phone(phone):
    phone = phone.replace('(', '').replace(' ', '').replace(')', '').replace('-', '').replace('_', '').replace('+', '')

    try:
        if len(phone) == 11:
            int(phone)
            return phone

        else:
            return False

    except:
        return False


def validate_card(card):
    card = card.replace(' ', '').replace('-', '').replace('_', '')

    try:
        if len(card) == 16:
            int(card)
            card = card[0:4] + ' ' + card[4:8] + ' ' + card[8:12] + ' ' + card[12:]
            return card

        else:
            return False

    except:
        return False
# регулярка (после слова)
def extract_referral_from_message(text):
    """Extracts referral from text."""

    regex = r'(?<=реферала )[a-zA-Z0-9]+'

    referral = re.search(regex, text).group()

    return referral


# формат чисел
def numbers_format(value):
    """Makes a good looking numbers format."""

    return '{:,}'.format(value).replace(',', ' ')