import telebot
from telebot import types
from Tools.markdown_constructor import *
from Core.Data import TaskViewInfo

# Buttons text:
from Tools.response_info import TASKS_LIST

RESET_KEY = 'Reset Key'
REMOVE_USER = 'Remove User'
ADD_USER = 'Add User'
LOGOUT = 'Logout'
USE_API = "Use API"

ADMIN = 'Admin'
USER = 'User'

CREATE_TASK = 'Create Task'
MODIFY_TASK = 'Modify Task'
GET_ALL_TASKS = 'Get All Tasks'

PREV = 'prev'
NEXT = 'next'


def display_task(bot: telebot.TeleBot, chat_id, task):
    content = get_bold_markdown(dict(task))
    bot.send_message(chat_id, content, parse_mode='MARKDOWN')


def display_tasks(bot: telebot.TeleBot, chat_id, response):
    tasks_list = response[TASKS_LIST]

    for i in range(len(tasks_list)):
        task = tasks_list[i]
        bot.send_message(chat_id, "*Task " + str(i) + "*:\n", parse_mode='MARKDOWN')
        display_task(bot, chat_id, task)


def get_choose_task_markup(info: TaskViewInfo, block_idx):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    task_block_info = info.tasks_info[block_idx]

    for info_text in task_block_info:
        markup.add(types.KeyboardButton(info_text))

    markup.add(types.KeyboardButton(NEXT))
    markup.add(types.KeyboardButton(PREV))

    return markup


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
        button3 = types.KeyboardButton(GET_ALL_TASKS)
        self.markup.row(button1, button2, button3)


chooseModeMarkup = ChooseModeMarkup().markup
chooseAdminActionMarkup = ChooseAdminActionMarkup().markup
chooseUserActionMarkup = ChooseUserActionMarkup().markup
chooseApiCommandMarkup = ChooseApiCommandMarkup().markup
