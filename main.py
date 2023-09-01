import telebot
import threading
import datetime

import db_functions
import config
import text
import utils
import functions
import keyboards


bot = telebot.TeleBot(config.TELEGRAM_TOKEN)


threading.Thread(daemon=True, target=functions.update_eligible).start()


@bot.message_handler(commands=['start', 'promo'])
def start_message(message):
    username = message.from_user.username
    user_id = message.from_user.id
    chat_id = message.chat.id

    if username:
        if not db_functions.is_in_database(user_id):
            db_functions.add_user(user_id, username)
            bot.send_message(chat_id=chat_id,
                             text=db_functions.get_text('start'),
                             reply_markup=keyboards.action_keyboard(),
                             parse_mode='Markdown',
                             )
        else:
            if db_functions.get_users_field_info(user_id, 'eligible_wb') or db_functions.get_users_field_info(user_id, 'eligible_ozon'):
                bot.send_message(chat_id=chat_id,
                             text=db_functions.get_text('start'),
                             reply_markup=keyboards.action_keyboard(),
                             parse_mode='Markdown',
                             )
            else:
                bot.send_message(chat_id=chat_id,
                                 text=text.PROHIBITED,
                                 parse_mode='Markdown',
                                 )
    
    else:
        bot.send_message(chat_id=chat_id,
                         text=text.USERNAME_NEEDED,
                         reply_markup=keyboards.ready_keyboard(),
                         parse_mode='Markdown',
                         )
    

@bot.message_handler(commands=['update'])
def update_message(message):
    user_id = str(message.from_user.id)

    if user_id in config.MANAGER_ID:
        threading.Thread(daemon=True, 
                            target=functions.update_database,
                            args=(user_id,) 
                            ).start()
    else:
        bot.send_message(chat_id=message.chat.id,
                         text=text.RESTRICTED,
                         parse_mode='Markdown',
                         )


@bot.message_handler(commands=['account'])
def update_message(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    payment_method = db_functions.get_users_field_info(user_id, 'payment_form')
    bank = db_functions.get_users_field_info(user_id, 'bank')
    account = db_functions.get_users_field_info(user_id, 'account')
    
    if payment_method and bank and account:
        reply_text = text.payment_method(payment_method, bank, account)

        bot.send_message(chat_id=chat_id,
                         text=reply_text,
                         parse_mode='Markdown',
                         )
    
    else:
        bot.send_message(chat_id=chat_id,
                         text=text.NO_PAYMENT_DATA,
                         parse_mode='Markdown',
                         )


@bot.message_handler(commands=['help'])
def help_message(message):
    chat_id = message.chat.id

    bot.send_message(chat_id=chat_id,
                     text=text.HELP,
                     reply_markup=keyboards.help_keyboard(),
                     parse_mode='Markdown',
                     )


@bot.message_handler(commands=['rules'])
def rules_message(message):
    reply_text = db_functions.get_text('rules')

    bot.send_message(chat_id=message.chat.id,
                     text=reply_text,
                     parse_mode='Markdown',
                     disable_web_page_preview=True,
                     )


@bot.callback_query_handler(func = lambda call: True)
def callback_query(call):
    """Handles queries from inline keyboards."""

    # getting message's and user's ids
    message_id = call.message.id
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    username = call.from_user.username

    call_data = call.data.split('_')
    query = call_data[0]

    if query == 'no':
        bot.edit_message_text(chat_id=chat_id,
                              message_id=message_id,
                              text=db_functions.get_text('sorry'),
                              parse_mode='Markdown',
                              )
    
    elif query == 'yes':
        bot.edit_message_text(chat_id=chat_id,
                              message_id=message_id,
                              text=db_functions.get_text('rules'),
                              parse_mode='Markdown',
                              disable_web_page_preview=True,
                              )
        
        bot.edit_message_reply_markup(chat_id=chat_id,
                                      message_id=message_id,
                                      reply_markup=keyboards.ready_keyboard(),
                                      )
    
    elif query == 'ready':
        wb_eligible = db_functions.get_users_field_info(user_id, 'eligible_wb')
        ozon_eligible = db_functions.get_users_field_info(user_id, 'eligible_ozon')

        bot.edit_message_text(chat_id=chat_id,
                              message_id=message_id,
                              text=text.CHOOSE_MARKETPLACE,
                              parse_mode='Markdown',
                              )
        
        bot.edit_message_reply_markup(chat_id=chat_id,
                                      message_id=message_id,
                                      reply_markup=keyboards.marketplace_keyboard(wb_eligible, ozon_eligible),
                                      )

    elif query == 'marketplace':
        marketplace = call_data[1]
        products = db_functions.select_active_products(marketplace)
        history = eval(db_functions.get_users_field_info(user_id, f'history_{marketplace}'))

        products_for_select = []
        for product in products:
            if product[1] not in history:
                products_for_select.append(product)
        
        if products_for_select:
            db_functions.drop_settings(user_id)

            try:
                bot.edit_message_reply_markup(chat_id=chat_id, 
                                              message_id=message_id,
                                              reply_markup=telebot.types.InlineKeyboardMarkup(),
                                              )
            except:
                pass
            
            group_media = []
            for product_photo in products_for_select:
                group_media.append(telebot.types.InputMediaPhoto(db_functions.select_products_photos(product_photo[1], marketplace)))

            bot.send_media_group(chat_id=chat_id,
                                 media=group_media,
                                 timeout=30,
                                 )

            bot.send_message(chat_id=chat_id,
                             text=db_functions.get_text('products'),
                             reply_markup=keyboards.products_keyboard(user_id, products_for_select, products, marketplace),
                             parse_mode='Markdown',
                             )

        else:
            db_functions.update_users_field(user_id, f'eligible_{marketplace}', False)
            bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text=text.ALREADY_ORDERED,
                                  parse_mode='Markdown',
                                  )

    elif query == 'username':
        if username:
            bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text=db_functions.get_text('start'),
                                  parse_mode='Markdown',
                                  )
            
            bot.edit_message_reply_markup(chat_id=chat_id,
                                          message_id=message_id,
                                          reply_markup=keyboards.action_keyboard(),
                                          )

    elif query == 'product':
        in_orders = int(call_data[1])
        current_product = int(call_data[2])
        product1 = int(call_data[3])
        product2 = int(call_data[4])
        marketplace = call_data[5]

        active_products = db_functions.select_active_products(marketplace)
        active_products_ids = list(dict(active_products).keys())

        if (current_product in active_products_ids) and\
        (product1 in active_products_ids) and (product2 in active_products_ids):
            history = eval(db_functions.get_users_field_info(user_id, f'history_{marketplace}'))
            products_for_select = []
            product_name = ''
            for product in active_products:
                if product[1] not in history:
                    products_for_select.append(product)

                if product[0] == current_product:
                    product_name = product[1]

            if products_for_select:
                users_products = eval(db_functions.get_users_field_info(user_id, 'products'))
                start_len = len(users_products)

                if in_orders:
                    users_products.remove(product_name)
                else:
                    if len(users_products) >= config.MAX_PRODUCTS and marketplace == 'wb':
                        bot.answer_callback_query(callback_query_id=call.id,
                                              text=text.MAX_LIMIT,
                                              show_alert=True,
                                              )                                       
                    else:
                        users_products.append(product_name)
                        

                if start_len != len(users_products):
                    db_functions.update_users_field(user_id, 'products', str(users_products))

                    bot.edit_message_text(chat_id=chat_id,
                                        message_id=message_id,
                                        text=db_functions.get_text('products'),
                                        parse_mode='Markdown',
                                        )
                    
                    bot.edit_message_reply_markup(chat_id=chat_id,
                                            message_id=message_id,
                                            reply_markup=keyboards.products_keyboard(user_id, products_for_select, active_products, marketplace),
                                            )
                    
            else:
                db_functions.update_users_field(user_id, f'eligible_{marketplace}', False)
                bot.edit_message_text(chat_id=chat_id,
                                    message_id=message_id,
                                    text=text.ALREADY_ORDERED,
                                    parse_mode='Markdown',
                                    )

        else:
            bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text=text.OUTDATED,
                                  parse_mode='Markdown',
                                  )
    
    elif query == 'done':
        product1 = int(call_data[1])
        product2 = int(call_data[2])
        product3 = int(call_data[3])
        marketplace = call_data[4]

        active_products = list(dict(db_functions.select_active_products(marketplace)).keys())

        if (product1 in active_products) and\
        (product2 in active_products) and (product3 in active_products):
            products = eval(db_functions.get_users_field_info(user_id, 'products'))

            if products:
                history = eval(db_functions.get_users_field_info(user_id, f'history_{marketplace}'))
                db_functions.update_users_field(user_id, f'history_{marketplace}', str(history + products))

                reply_text, smiles = text.bought_products(products)

                for product in products:
                    product_id = db_functions.select_products_id(product, marketplace)
                    counter = db_functions.get_products_field_info(product_id, 'counter')

                    if counter is not None:
                        counter -= 1
                        db_functions.update_product_field(product_id, 'counter', counter)

                        if counter == 0:
                            db_functions.update_product_field(product_id, 'active', False)

                db_functions.update_users_field(user_id, 'smiles', smiles)
                db_functions.update_users_field(user_id, 'eligible_wb', False)
                db_functions.update_users_field(user_id, 'eligible_ozon', False)
                db_functions.update_users_field(user_id, f'last_participate_{marketplace}', datetime.datetime.utcnow())
                db_functions.update_users_field(user_id, 'input', True)
                db_functions.update_users_field(user_id, 'input_data', 'receive_0')
                db_functions.update_users_field(user_id, 'marketplace', marketplace)

                bot.edit_message_text(chat_id=chat_id,
                                    message_id=message_id,
                                    text=reply_text,
                                    parse_mode='Markdown',
                                    )

        else:
            bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text=text.OUTDATED,
                                  parse_mode='Markdown',
                                  )
    
    elif query == 'received':
        bot.edit_message_reply_markup(chat_id=chat_id,
                                      message_id=message_id,
                                      reply_markup=telebot.types.InlineKeyboardMarkup(),
                                      )

        db_functions.update_users_field(user_id, 'input', True)
        db_functions.update_users_field(user_id, 'input_data', 'review_0')

        products = eval(db_functions.get_users_field_info(user_id, 'products'))
        smile = db_functions.get_users_field_info(user_id, 'smiles')[0]
        reply_text = text.review_product(utils.escape_markdown(products[0]), smile)

        bot.send_message(chat_id=chat_id,
                        text=reply_text,
                        parse_mode='Markdown',
                        )
    
    elif query == 'back':
        destination = call_data[1]

        if destination == 'method':
            db_functions.update_users_field(user_id, 'payment_form', None)
            db_functions.update_users_field(user_id, 'input_data', 'payment_method')

            bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text=text.PAYMENT_METHOD,
                                  parse_mode='Markdown',
                                  )
            
            bot.edit_message_reply_markup(chat_id=chat_id,
                                          message_id=message_id,
                                          reply_markup=keyboards.payment_method_keyboard(),
                                          )
    
    elif query == 'method':
        method = call_data[1]

        if db_functions.get_users_field_info(user_id, 'input') and\
        db_functions.get_users_field_info(user_id, 'input_data') == 'payment_method':
            db_functions.update_users_field(user_id, 'payment_form', method)
            db_functions.update_users_field(user_id, 'input_data', 'bank')

            bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text=text.BANK,
                                  parse_mode='Markdown',
                                  )
            
            bot.edit_message_reply_markup(chat_id=chat_id,
                                          message_id=message_id,
                                          reply_markup=keyboards.banks_keyboard(),
                                          )
    
    elif query == 'bank':
        bank = call_data[1]

        if db_functions.get_users_field_info(user_id, 'input') and\
        db_functions.get_users_field_info(user_id, 'input_data') == 'bank':
            db_functions.update_users_field(user_id, 'bank', bank)
            
            payment_method = db_functions.get_users_field_info(user_id, 'payment_form')

            if payment_method == 'card':
                db_functions.update_users_field(user_id, 'input_data', 'account_card')
                bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text=text.CARD,
                                  parse_mode='Markdown',
                                  )

            elif payment_method == 'sbp':
                db_functions.update_users_field(user_id, 'input_data', 'account_phone')
                bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text=text.PHONE,
                                  parse_mode='Markdown',
                                  )
    
    elif query == 'reenter':
        db_functions.update_users_field(user_id, 'account', None)
        db_functions.update_users_field(user_id, 'bank', None)
        db_functions.update_users_field(user_id, 'payment_form', None)
        db_functions.update_users_field(user_id, 'input', True)
        db_functions.update_users_field(user_id, 'input_data', 'payment_method')

        bot.edit_message_text(chat_id=chat_id,
                              message_id=message_id,
                              text=text.PAYMENT_METHOD,
                              parse_mode='Markdown',
                              )
        
        bot.edit_message_reply_markup(chat_id=chat_id,
                                      message_id=message_id,
                                      reply_markup=keyboards.payment_method_keyboard(),
                                      )
    
    elif query == 'confirm':
        threading.Thread(daemon=True, 
                            target=functions.inform_manager,
                            args=(user_id,) 
                            ).start()
        marketplace = db_functions.get_users_field_info(user_id, 'marketplace')

        if marketplace == 'wb':
            last_participate_ozon = db_functions.get_users_field_info(user_id, 'last_participate_ozon')
            if last_participate_ozon is None or\
            (last_participate_ozon and last_participate_ozon < datetime.datetime.utcnow - datetime.timedelta(days=7)):
                db_functions.update_users_field(user_id, 'eligible_ozon', True)
        
        elif marketplace == 'ozon':
            last_participate_wb = db_functions.get_users_field_info(user_id, 'last_participate_wb')
            if last_participate_wb is None or\
            (last_participate_wb and last_participate_wb < datetime.datetime.utcnow - datetime.timedelta(days=7)):
                db_functions.update_users_field(user_id, 'eligible_wb', True)

        bot.edit_message_text(chat_id=chat_id,
                              message_id=message_id,
                              text=text.DONE,
                              parse_mode='Markdown',
                              )
    
    elif query == 'help':
        answer = call_data[1]

        if answer == 'yes':
            if username:
                try:
                    bot.send_message(chat_id=config.MANAGER_ID,
                                     text=text.asked_help(username),
                                     )
                except:
                    pass

                bot.edit_message_text(chat_id=chat_id,
                                      message_id=message_id,
                                      text=text.ADMIN_INFORMED,
                                      parse_mode='Markdown',
                                      )

            else:
                bot.edit_message_text(chat_id=chat_id,
                                      message_id=message_id,
                                      text=text.NO_USERNAME,
                                      parse_mode='Markdown',
                                      )
                
                bot.edit_message_reply_markup(chat_id=chat_id,
                                              message_id=message_id,
                                              reply_markup=keyboards.update_keyboard(),
                                              )
        
        elif answer == 'no':
            bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text=text.NO_HELP,
                                  parse_mode='Markdown',
                                  )
    
    elif query == 'update':
        if username:
            try:
                bot.send_message(chat_id=config.MANAGER_ID,
                                 text=text.asked_help(username),
                                 )
            except:
                pass

            bot.edit_message_text(chat_id=chat_id,
                                      message_id=message_id,
                                      text=text.ADMIN_INFORMED,
                                      parse_mode='Markdown',
                                      )


@bot.message_handler(content_types=['photo'])
def handle_text(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    media_group_id = message.media_group_id
    input = db_functions.get_users_field_info(user_id, 'input')
    input_data = db_functions.get_users_field_info(user_id, 'input_data')

    if not media_group_id:
        if input and 'receive' in input_data:
            products = eval(db_functions.get_users_field_info(user_id, 'products'))
            current_receive = eval(db_functions.get_users_field_info(user_id, 'receive'))
            current_receive.append(message.photo[-1].file_id)
            db_functions.update_users_field(user_id, 'receive', str(current_receive))

            if len(products) == len(current_receive):
                threading.Thread(daemon=True, 
                            target=functions.inform_manager_bought,
                            args=(user_id,) 
                            ).start()

                db_functions.update_users_field(user_id, 'input', False)
                db_functions.update_users_field(user_id, 'input_data', None)

                smiles = db_functions.get_users_field_info(user_id, 'smiles')
                
                reply_text = text.when_receive(products, smiles)

                bot.send_message(chat_id=chat_id,
                                text=reply_text,
                                reply_markup=keyboards.received_keyboard(),
                                parse_mode='Markdown',
                                )

            else:
                index = int(input_data.split('_')[1]) + 1
                db_functions.update_users_field(user_id, 'input_data', f'receive_{index}')
                reply_text = text.receive_product(utils.escape_markdown(products[index]))

                bot.send_message(chat_id=chat_id,
                                text=reply_text,
                                parse_mode='Markdown',
                                )

        elif input and 'review' in input_data:
            products = eval(db_functions.get_users_field_info(user_id, 'products'))
            current_review = eval(db_functions.get_users_field_info(user_id, 'review'))
            current_review.append(message.photo[-1].file_id)
            db_functions.update_users_field(user_id, 'review', str(current_review))

            if len(products) == len(current_review):
                payment_method = db_functions.get_users_field_info(user_id, 'payment_form')
                bank = db_functions.get_users_field_info(user_id, 'bank')
                account = db_functions.get_users_field_info(user_id, 'account')

                if payment_method and bank and account:
                    reply_text = text.payment_method(payment_method, bank, account)

                    bot.send_message(chat_id=chat_id,
                                    text=reply_text,
                                    reply_markup=keyboards.confirm_keyboard(),
                                    parse_mode='Markdown',
                                    )

                else:
                    db_functions.update_users_field(user_id, 'input_data', 'payment_method')

                    bot.send_message(chat_id=chat_id,
                                    text=text.PAYMENT_METHOD,
                                    reply_markup=keyboards.payment_method_keyboard(),
                                    parse_mode='Markdown',
                                    )

            else:
                index = int(input_data.split('_')[1]) + 1
                smiles = db_functions.get_users_field_info(user_id, 'smiles')
                db_functions.update_users_field(user_id, 'input_data', f'review_{index}')
                reply_text = text.review_product(utils.escape_markdown(products[index]), smiles[index])

                bot.send_message(chat_id=chat_id,
                                text=reply_text,
                                parse_mode='Markdown',
                                )
        
        else:
            bot.send_message(chat_id=chat_id,
                         text=text.IS_HELD_NEEDED,
                         parse_mode='Markdown',
                         )
        
    else:
        bot.send_message(chat_id=chat_id,
                         text=text.NO_MEDIA_GROUP,
                         parse_mode='Markdown',
                         )


@bot.message_handler(content_types=['document'])
def handle_text(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    input = db_functions.get_users_field_info(user_id, 'input')
    input_data = db_functions.get_users_field_info(user_id, 'input_data')

    if input and ('receive' in input_data or 'review' in input_data):
        bot.send_message(chat_id=chat_id,
                         text=text.NO_DOCUMENT,
                         parse_mode='Markdown',
                         )
    else:
        bot.send_message(chat_id=chat_id,
                         text=text.IS_HELD_NEEDED,
                         parse_mode='Markdown',
                         )


@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    input = db_functions.get_users_field_info(user_id, 'input')
    input_data = db_functions.get_users_field_info(user_id, 'input_data')

    if input and 'account' in input_data:
        if 'phone' in input_data:
            account = utils.validate_phone(message.text)
        elif 'card' in input_data:
            account = utils.validate_card(message.text)

        if account:
            db_functions.update_users_field(user_id, 'account', account)
            db_functions.update_users_field(user_id, 'input', False)
            db_functions.update_users_field(user_id, 'input_data', None)

            payment_method = db_functions.get_users_field_info(user_id, 'payment_form')
            bank = db_functions.get_users_field_info(user_id, 'bank')
            account = db_functions.get_users_field_info(user_id, 'account')

            reply_text = text.payment_method(payment_method, bank, account)

            bot.send_message(chat_id=chat_id,
                             text=reply_text,
                             reply_markup=keyboards.confirm_keyboard(),
                             parse_mode='Markdown',
                             )

        else:
            bot.send_message(chat_id=chat_id,
                                text=text.WRONG_FORMAT,
                                parse_mode='Markdown',
                                )
    
    else:
        bot.send_message(chat_id=chat_id,
                         text=text.IS_HELD_NEEDED,
                         parse_mode='Markdown',
                         )


if __name__ == '__main__':
    # bot.polling(timeout=80)
    while True:
        try:
            bot.polling()
        except:
            pass