from Core.handlers import *


class Bot(object):
    def __init__(self, api_key):
        self.bot = telebot.TeleBot(api_key, parse_mode=None)
        self.bot_info = BotInfo()
        self.setup()

    def setup(self):
        bot = self.bot

        @bot.message_handler(func=self.is_not_started, commands=['start'])
        def send_welcome(message):
            bot_info = self.bot_info
            bot_info.set_chat_id(message.chat.id)
            bot_info.mode = Mode.LOGIN
            bot_info.is_started = True

            bot.send_message(bot_info.chat_id, "choose mode: 'Admin' or 'User'", reply_markup=chooseModeMarkup)

        @bot.message_handler(func=self.is_started)
        def handle_all(message):
            bot_info = self.bot_info
            try:
                # depended on bot state call the appropriate handlers
                if bot_info.mode == Mode.LOGIN:
                    handle_login_message(message, bot, bot_info)
                elif bot_info.mode == Mode.ADMIN:
                    if bot_info.state == AdminState.AUTHENTICATION:
                        handle_admin_authentication(message, bot, bot_info)
                    elif bot_info.state == AdminState.CHOOSE_ACTION:
                        handle_admin_choose_action(message, bot, bot_info)
                    elif bot_info.state == AdminState.RESET_KEY:
                        handle_admin_reset_key(message, bot, bot_info)
                    elif bot_info.state == AdminState.ADD_USER:
                        handle_admin_add_user(message, bot, bot_info)
                    elif bot_info.state == AdminState.REMOVE_USER:
                        handle_admin_remove_user(message, bot, bot_info)
                elif bot_info.mode == Mode.USER:
                    if bot_info.state == UserState.AUTHENTICATION:
                        handle_user_authentication(message, bot, bot_info)
                    elif bot_info.state == UserState.CHOOSE_ACTION:
                        handle_user_choose_action(message, bot, bot_info)
                    elif bot_info.state == UserState.USE_API:
                        handle_user_choose_api_command(message, bot, bot_info)
                    elif bot_info.state == UserState.CREATE_TASK:
                        handle_user_api_create_task(message, bot, bot_info)
                else:
                    assert False
            except Exception as e:
                bot.send_message(bot_info.chat_id, str(e.args))

    def is_started(self, msg):
        return self.bot_info.is_started

    def is_not_started(self, msg):
        return not self.bot_info.is_started
