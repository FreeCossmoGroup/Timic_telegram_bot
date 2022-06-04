from telebot import types

# Buttons text:
RESET_KEY = 'Reset Key'
REMOVE_USER = 'Remove User'
ADD_USER = 'Add User'
LOGOUT = 'Logout'
USE_API = "Use API"

ADMIN = 'Admin'
USER = 'User'

CREATE_TASK = 'Create Task'
MODIFY_TASK = 'Modify Task'


class ChooseModeMarkup(object):
    def __init__(self):
        self.markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        button1 = types.KeyboardButton(ADMIN)
        button2 = types.KeyboardButton(USER)
        self.markup.row(button1, button2)


class ChooseAdminActionMarkup(object):
    def __init__(self):
        self.markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        button1 = types.KeyboardButton(RESET_KEY)
        button2 = types.KeyboardButton(REMOVE_USER)
        button3 = types.KeyboardButton(ADD_USER)
        button4 = types.KeyboardButton(LOGOUT)
        self.markup.row(button1, button2, button3, button4)


class ChooseUserActionMarkup(object):
    def __init__(self):
        self.markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        button1 = types.KeyboardButton(USE_API)
        button2 = types.KeyboardButton(LOGOUT)
        self.markup.row(button1, button2)


class ChooseApiCommandMarkup(object):
    def __init__(self):
        self.markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        button1 = types.KeyboardButton(CREATE_TASK)
        button2 = types.KeyboardButton(MODIFY_TASK)
        self.markup.row(button1, button2)


chooseModeMarkup = ChooseModeMarkup().markup
chooseAdminActionMarkup = ChooseAdminActionMarkup().markup
chooseUserActionMarkup = ChooseUserActionMarkup().markup
chooseApiCommandMarkup = ChooseApiCommandMarkup().markup