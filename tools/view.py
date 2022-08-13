import telebot
from telebot import types
from core.data import TaskViewInfo, start_time_response
from core.data import id

# Buttons text:
from tools.response_info import TASKS_LIST

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

PREV = '<<'
NEXT = '>>'

DONE = 'Done'


def display_task(bot: telebot.TeleBot, chat_id, task):
    # returns list of attributes as a markdown
    def get_bold_markdown(attributes: dict):
        markdown_str = ""
        for attr in attributes:
            markdown_str += "*" + attr + "* - " + str(attributes[attr]) + "\n"

        return markdown_str

    content = get_bold_markdown(dict(task))
    bot.send_message(chat_id, content, parse_mode='MARKDOWN')


def display_tasks(bot: telebot.TeleBot, chat_id, response):
    tasks_list = response[TASKS_LIST]

    for i in range(len(tasks_list)):
        task = tasks_list[i]
        bot.send_message(chat_id, "*Task " + str(i) + "*:\n", parse_mode='MARKDOWN')
        display_task(bot, chat_id, task)


# dont display 'id' attribute and 'startTime' attribute
def get_task_attributes_markup(task):
    # task is a dict, task attributes - its elements

    def get_attr_view_info(attr_idx):
        max_char_count = 18
        attribute = key_list[attr_idx]
        return str(attribute) + ": " + str(task[attribute])[:max_char_count]

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)

    task.pop(id)                     # remove id attribute
    task.pop(start_time_response)    # remove start time attribute

    attr_count = len(task)
    key_list = list(task)

    if attr_count % 2 == 0:
        last_row = [types.KeyboardButton(DONE)]
    else:
        last_row = [types.KeyboardButton(get_attr_view_info(attr_count - 1)), types.KeyboardButton(DONE)]

    for row in range(attr_count // 2):
        button1 = types.KeyboardButton(get_attr_view_info(row * 2))
        button2 = types.KeyboardButton(get_attr_view_info(row * 2 + 1))
        markup.row(button1, button2)

    markup.row(*last_row)

    return markup


def get_choose_task_markup(info: TaskViewInfo, block_idx):
    task_block_info = info.tasks_info[block_idx]

    row_size = 2                          # count of buttons in one row
    block_size = len(task_block_info)     # count of tasks in current block
    row_count = (block_size // row_size) + (block_size % row_size > 0)

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)

    for row_idx in range(row_count):
        start_task_idx = row_idx * row_size
        buttons_list = []

        # add tasks text:
        for col_idx in range(row_size):
            cur_task_idx = start_task_idx + col_idx
            buttons_list.append(types.KeyboardButton(task_block_info[cur_task_idx]))

            if cur_task_idx == block_size - 1:
                break

        if row_idx == row_count // 2 or row_count == 1:
            # add PREV and NEXT buttons
            buttons_list.insert(row_size, types.KeyboardButton(NEXT))
            buttons_list.insert(0, types.KeyboardButton(PREV))

        # add created row to the markup
        markup.row(*buttons_list)
    markup.row(types.KeyboardButton(DONE))  # add DOWN button to the bottom

    return markup


def get_choose_mode_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button1 = types.KeyboardButton(ADMIN)
    button2 = types.KeyboardButton(USER)
    markup.row(button1, button2)

    return markup


def get_choose_admin_action_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button1 = types.KeyboardButton(RESET_KEY)
    button2 = types.KeyboardButton(REMOVE_USER)
    button3 = types.KeyboardButton(ADD_USER)
    button4 = types.KeyboardButton(LOGOUT)
    markup.row(button1, button2, button3, button4)

    return markup


def get_choose_user_action_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button1 = types.KeyboardButton(USE_API)
    button2 = types.KeyboardButton(LOGOUT)
    markup.row(button1, button2)

    return markup


def get_choose_api_command_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button1 = types.KeyboardButton(CREATE_TASK)
    button2 = types.KeyboardButton(MODIFY_TASK)
    button3 = types.KeyboardButton(GET_ALL_TASKS)
    markup.row(button1, button2, button3)

    return markup


chooseModeMarkup = get_choose_mode_markup()
chooseAdminActionMarkup = get_choose_admin_action_markup()
chooseUserActionMarkup = get_choose_user_action_markup()
chooseApiCommandMarkup = get_choose_api_command_markup()
