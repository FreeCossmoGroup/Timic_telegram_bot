from Core.Data import Mode, UserState, AdminState, BotInfo
from Tools.config import save_config_from_bot
import telebot

from Tools.View import *


def handle_login_message(message, bot: telebot.TeleBot, bot_info: BotInfo):
    text = message.text
    if text == USER:
        if bot_info.user_table.get_size() <= 0:
            bot.send_message(bot_info.chat_id, "no users created yet. Choose 'Admin' mode and create one")
            bot.send_message(bot_info.chat_id, "choose mode: 'Admin' or 'User'", reply_markup=chooseModeMarkup)
        else:
            bot_info.change_handler_info(Mode.USER, UserState.AUTHENTICATION)
            bot.send_message(bot_info.chat_id, "you chosen 'User' mode")
            bot.send_message(bot_info.chat_id, "enter username and password in format - username 'space' password:")
    elif text == ADMIN:
        bot_info.change_handler_info(Mode.ADMIN, AdminState.AUTHENTICATION)
        bot.send_message(bot_info.chat_id, "you chosen 'Admin' mode")
        bot.send_message(bot_info.chat_id, "enter the admin key:")
    else:
        raise Exception("choose suggested mode")


def handle_admin_authentication(message, bot: telebot.TeleBot, bot_info: BotInfo):
    admin_key = message.text

    if admin_key != bot_info.admin_key:
        bot.send_message(bot_info.chat_id, "invalid admin key. authentication failed")
        bot.send_message(bot_info.chat_id, "enter the admin key:")
    else:
        bot.send_message(bot_info.chat_id, "authentication succeed")
        bot_info.change_handler_info(Mode.ADMIN, AdminState.CHOOSE_ACTION)
        bot.send_message(bot_info.chat_id, "choose action:", reply_markup=chooseAdminActionMarkup)


def handle_admin_choose_action(message, bot: telebot.TeleBot, bot_info: BotInfo):
    text = message.text

    if text == RESET_KEY:
        bot_info.change_handler_info(Mode.ADMIN, AdminState.RESET_KEY)
        bot.send_message(bot_info.chat_id, "enter new admin key:")
    elif text == REMOVE_USER:
        if bot_info.user_table.get_size() == 0:
            bot.send_message(bot_info.chat_id, "no users yet. Add some by 'Add User' command")
            bot_info.change_handler_info(Mode.ADMIN, AdminState.CHOOSE_ACTION)
        else:
            bot_info.change_handler_info(Mode.ADMIN, AdminState.REMOVE_USER)
            bot.send_message(bot_info.chat_id, "enter the user's id you want to remove:")
    elif text == ADD_USER:
        bot_info.change_handler_info(Mode.ADMIN, AdminState.ADD_USER)
        bot.send_message(bot_info.chat_id, "enter username and password in format - username 'space' password:")
    elif text == LOGOUT:
        bot_info.change_handler_info(Mode.LOGIN, None)
        bot.send_message(bot_info.chat_id, "logout from 'Admin'")
        bot.send_message(bot_info.chat_id, "choose mode: 'Admin' or 'User'", reply_markup=chooseModeMarkup)
    else:
        raise Exception("choose suggested command")


def handle_admin_add_user(message, bot: telebot.TeleBot, bot_info: BotInfo):
    text = message.text
    tokens = text.split()
    tokens_count = len(tokens)

    if tokens_count != 2:
        bot.send_message(bot_info.chat_id, str(tokens_count) + " words got, should be 2 - 'username', 'password'")
        bot.send_message(bot_info.chat_id, "enter username and password in format - username 'space' password:")
    else:
        if bot_info.user_table.get_user_by_name(tokens[0]) != -1:
            bot.send_message(bot_info.chat_id, "user with name: " + tokens[1] + " already exists")
            bot.send_message(bot_info.chat_id, "enter username and password in format - username 'space' password:")
        else:
            user_id = bot_info.user_table.add_user(tokens[0], tokens[1])
            save_config_from_bot(bot_info)
            bot_info.change_handler_info(Mode.ADMIN, AdminState.CHOOSE_ACTION)
            bot.send_message(bot_info.chat_id, "user successfully added, id=" + str(user_id),
                             reply_markup=chooseAdminActionMarkup)


def handle_admin_remove_user(message, bot: telebot.TeleBot, bot_info: BotInfo):
    text = message.text
    id = -1
    try:
        id = int(str(text))
    except ValueError:
        bot.send_message(bot_info.chat_id, "invalid id: " + text)
        bot.send_message(bot_info.chat_id, "enter the user's id you want to remove:")

    if not (id in bot_info.user_table.users):
        bot.send_message(bot_info.chat_id, "no user with id " + str(id))
        bot.send_message(bot_info.chat_id, "enter the user's id you want to remove:")
    else:
        bot_info.user_table.remove_user(id)
        save_config_from_bot(bot_info)
        bot_info.change_handler_info(Mode.ADMIN, AdminState.CHOOSE_ACTION)
        bot.send_message(bot_info.chat_id, "user with id " + str(id) + " successfully deleted",
                         reply_markup=chooseAdminActionMarkup)


def handle_admin_reset_key(message, bot: telebot.TeleBot, bot_info: BotInfo):
    key = message.text
    bot_info.admin_key = key
    save_config_from_bot(bot_info)

    bot_info.change_handler_info(Mode.ADMIN, AdminState.CHOOSE_ACTION)
    bot.send_message(bot_info.chat_id, "new Admin key is set", reply_markup=chooseAdminActionMarkup)


# user handlers:

def handle_user_choose_action(message, bot: telebot.TeleBot, bot_info: BotInfo):
    text = message.text

    if text == USE_API:
        bot_info.change_handler_info(Mode.USER, UserState.USE_API)
        bot.send_message(bot_info.chat_id, "choose command:")
    elif text == LOGOUT:
        bot_info.change_handler_info(Mode.LOGIN, None)
        bot.send_message(bot_info.chat_id, "logout from 'User'", reply_markup=chooseModeMarkup)
    else:
        raise Exception("choose suggested command")


def handle_user_authentication(message, bot: telebot.TeleBot, bot_info: BotInfo):
    text = message.text
    tokens = text.split()
    tokens_count = len(tokens)

    if tokens_count != 2:
        bot.send_message(bot_info.chat_id, str(tokens_count) + " words got, should be 2 - 'username', 'password'")
        bot.send_message(bot_info.chat_id, "enter username and password in format - username 'space' password:")
    else:
        username = tokens[0]
        password = tokens[1]
        user_id = bot_info.user_table.get_user_by_name(username)
        user = bot_info.user_table.get_user(user_id)

        if user_id == -1:
            bot.send_message(bot_info.chat_id, "user with name " + username + " doesn't exists")
            bot.send_message(bot_info.chat_id, "enter username and password in format - username 'space' password:")
        else:
            if user.password != password:
                bot.send_message(bot_info.chat_id, "invalid password")
                bot.send_message(bot_info.chat_id, "enter username and password in format - username 'space' password:")
            else:
                bot_info.change_handler_info(Mode.USER, UserState.CHOOSE_ACTION)
                bot.send_message(bot_info.chat_id, "authentication succeed", reply_markup=chooseUserActionMarkup)
