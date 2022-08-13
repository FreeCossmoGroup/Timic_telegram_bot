from core.data import *
from tools.config import save_config_from_bot
from tools.view import *
from web.api_requests import *
from tools.response_info import *

login_message = "enter username and password in format - username 'space' password:"


class Bot(object):
    def __init__(self, api_key):
        self.bot = telebot.TeleBot(api_key, parse_mode=None)
        self.bot_info = BotInfo()
        self.setup()

    def setup(self):
        bot = self.bot

        @bot.message_handler(func=lambda _: self.is_not_started(), commands=['start'])
        def send_welcome(message):
            bot_info = self.bot_info
            bot_info.set_chat_id(message.chat.id)
            bot_info.mode = Mode.LOGIN
            bot_info.is_started = True

            bot.send_message(bot_info.chat_id, "choose mode: 'Admin' or 'User'", reply_markup=chooseModeMarkup)

        @bot.message_handler(func=lambda _: self.is_started())
        def handle_all(message):

            def handle_admin(message, bot: Bot):
                bot_info = bot.bot_info

                if bot_info.state == AdminState.AUTHENTICATION:
                    handle_admin_authentication(message, bot)
                elif bot_info.state == AdminState.CHOOSE_ACTION:
                    handle_admin_choose_action(message, bot)
                elif bot_info.state == AdminState.RESET_KEY:
                    handle_admin_reset_key(message, bot)
                elif bot_info.state == AdminState.ADD_USER:
                    handle_admin_add_user(message, bot)
                elif bot_info.state == AdminState.REMOVE_USER:
                    handle_admin_remove_user(message, bot)

            def handle_user(message, bot: Bot):
                bot_info = bot.bot_info

                if bot_info.state == UserState.AUTHENTICATION:
                    handle_user_authentication(message, bot)
                elif bot_info.state == UserState.CHOOSE_ACTION:
                    handle_user_choose_action(message, bot)
                elif bot_info.state == UserState.USE_API:
                    handle_user_choose_api_command(message, bot)
                elif bot_info.state == UserState.CREATE_TASK:
                    handle_user_api_create_task(message, bot)
                elif bot_info.state == UserState.MODIFY_TASK:
                    handle_user_api_modify_task(message, bot)
                elif bot_info.state == UserState.MODIFY_TASK_PROCESS:
                    handle_user_api_modify_task_process(message, bot)
                elif bot_info.state == UserState.SET_ATTRIBUTE_VALUE:
                    handle_user_api_set_attribute(message, bot)

            bot_info = self.bot_info
            try:
                # depended on bot Mode call the appropriate handlers
                if bot_info.mode == Mode.LOGIN:
                    handle_login_message(message, self)
                elif bot_info.mode == Mode.ADMIN:
                    handle_admin(message, self)
                elif bot_info.mode == Mode.USER:
                    handle_user(message, self)
                else:
                    assert False
            except Exception as e:
                bot.send_message(bot_info.chat_id, str(e.args))

    def is_started(self):
        return self.bot_info.is_started

    def is_not_started(self):
        return not self.bot_info.is_started


def handle_login_message(message, bot_wrapper: Bot):
    bot_info = bot_wrapper.bot_info
    bot = bot_wrapper.bot

    text = message.text
    if text == USER:
        if bot_info.user_table.get_size() <= 0:
            bot.send_message(bot_info.chat_id, "no users created yet. Choose 'Admin' mode and create one")
            bot.send_message(bot_info.chat_id, "choose mode: 'Admin' or 'User'", reply_markup=chooseModeMarkup)
        else:
            bot_info.change_handler_info(Mode.USER, UserState.AUTHENTICATION)
            bot.send_message(bot_info.chat_id, "you chosen 'User' mode")
            bot.send_message(bot_info.chat_id, login_message)
    elif text == ADMIN:
        bot_info.change_handler_info(Mode.ADMIN, AdminState.AUTHENTICATION)
        bot.send_message(bot_info.chat_id, "you chosen 'Admin' mode")
        bot.send_message(bot_info.chat_id, "enter the admin key:")
    else:
        bot.send_message(bot_info.chat_id, "choose suggested mode:", reply_markup=chooseModeMarkup)


def handle_admin_authentication(message, bot_wrapper: Bot):
    bot_info = bot_wrapper.bot_info
    bot = bot_wrapper.bot
    admin_key = message.text

    if admin_key != bot_info.admin_key:
        bot.send_message(bot_info.chat_id, "invalid admin key. authentication failed")
        bot.send_message(bot_info.chat_id, "enter the admin key:")
    else:
        bot.send_message(bot_info.chat_id, "authentication succeed")
        bot_info.change_handler_info(Mode.ADMIN, AdminState.CHOOSE_ACTION)
        bot.send_message(bot_info.chat_id, "choose action:", reply_markup=chooseAdminActionMarkup)


def handle_admin_choose_action(message, bot_wrapper: Bot):
    bot_info = bot_wrapper.bot_info
    bot = bot_wrapper.bot
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
            bot.send_message(bot_info.chat_id, "enter the user's name you want to remove:")
    elif text == ADD_USER:
        bot_info.change_handler_info(Mode.ADMIN, AdminState.ADD_USER)
        bot.send_message(bot_info.chat_id, login_message)
    elif text == LOGOUT:
        bot_info.change_handler_info(Mode.LOGIN, None)
        bot.send_message(bot_info.chat_id, "logout from 'Admin'")
        bot.send_message(bot_info.chat_id, "choose mode: 'Admin' or 'User'", reply_markup=chooseModeMarkup)
    else:
        bot.send_message(bot_info.chat_id, "choose suggested command:", reply_markup=chooseAdminActionMarkup)
        bot.send_message(bot_info.chat_id, "choose suggested command:", reply_markup=chooseAdminActionMarkup)


def handle_admin_add_user(message, bot_wrapper: Bot):
    bot_info = bot_wrapper.bot_info
    bot = bot_wrapper.bot

    text = message.text
    tokens = text.split()
    tokens_count = len(tokens)

    if tokens_count != 2:
        bot.send_message(bot_info.chat_id, str(tokens_count) + " words got, should be 2 - 'username', 'password'")
        bot.send_message(bot_info.chat_id, login_message)
    else:
        name = tokens[0]
        pswd = tokens[1]

        if bot_info.user_table.add_user(name, pswd):
            # user successfully added
            save_config_from_bot(bot_info)
            bot_info.change_handler_info(Mode.ADMIN, AdminState.CHOOSE_ACTION)
            bot.send_message(bot_info.chat_id, "user successfully added, name=" + str(name),
                             reply_markup=chooseAdminActionMarkup)
        else:
            # user with this name already exists
            bot.send_message(bot_info.chat_id, "user with name: " + name + " already exists")
            bot.send_message(bot_info.chat_id, login_message)


def handle_admin_remove_user(message, bot_wrapper: Bot):
    bot_info = bot_wrapper.bot_info
    bot = bot_wrapper.bot

    name = message.text

    if len(name.split()) != 1:
        bot.send_message(bot_info.chat_id, "you should type one word - user name. got: " + name)

    elif bot_info.user_table.remove_user(name):
        # user successfully removed
        save_config_from_bot(bot_info)
        bot_info.change_handler_info(Mode.ADMIN, AdminState.CHOOSE_ACTION)
        bot.send_message(bot_info.chat_id, "user with name '" + name + "' successfully deleted",
                         reply_markup=chooseAdminActionMarkup)
    else:
        bot.send_message(bot_info.chat_id, "no user with such name - '" + name + "'")
        bot.send_message(bot_info.chat_id, "enter the user's name you want to remove:")


def handle_admin_reset_key(message, bot_wrapper: Bot):
    bot_info = bot_wrapper.bot_info
    bot = bot_wrapper.bot

    key = message.text
    bot_info.admin_key = key
    save_config_from_bot(bot_info)

    bot_info.change_handler_info(Mode.ADMIN, AdminState.CHOOSE_ACTION)
    bot.send_message(bot_info.chat_id, "new Admin key is set", reply_markup=chooseAdminActionMarkup)


# user handlers:
def handle_user_choose_action(message, bot_wrapper: Bot):
    bot_info = bot_wrapper.bot_info
    bot = bot_wrapper.bot

    text = message.text

    if text == USE_API:
        bot_info.change_handler_info(Mode.USER, UserState.USE_API)
        bot.send_message(bot_info.chat_id, "choose command:", reply_markup=chooseApiCommandMarkup)
    elif text == LOGOUT:
        bot_info.change_handler_info(Mode.LOGIN, None)
        bot.send_message(bot_info.chat_id, "logout from 'User'", reply_markup=chooseModeMarkup)
    else:
        bot.send_message(bot_info.chat_id, "choose suggested command:", reply_markup=chooseUserActionMarkup)


def handle_user_choose_api_command(message, bot_wrapper: Bot):
    bot_info = bot_wrapper.bot_info
    bot = bot_wrapper.bot

    text = message.text

    if text == CREATE_TASK:
        bot_info.query_info = QueryInfo(QueryType.CREATE_TASK)
        bot_info.change_handler_info(Mode.USER, UserState.CREATE_TASK)
        bot.send_message(bot_info.chat_id, "enter " + str(bot_info.query_info.get_cur_parameter()) + ":")

    elif text == GET_ALL_TASKS:
        bot.send_message(bot_info.chat_id, "**created tasks:**", parse_mode='MARKDOWN')
        handle_user_api_get_all_tasks(bot_wrapper)

    elif text == MODIFY_TASK:
        bot_info.query_info = QueryInfo(QueryType.MODIFY_TASK)
        bot_info.change_handler_info(Mode.USER, UserState.MODIFY_TASK)

        # get display info for all tasks:
        response = get_all_tasks()
        tasks = response[TASKS_LIST]

        bot_info.tasks_view_info = TaskViewInfo(tasks)
        bot_info.tasks_list = tasks

        first_block_idx = 0

        bot.send_message(bot_info.chat_id, "choose task you want to modify:",
                         reply_markup=get_choose_task_markup(bot_info.tasks_view_info, first_block_idx))
    else:
        bot.send_message(bot_info.chat_id, "invalid API command - " + text + "; choose suggested:",
                         reply_markup=chooseUserActionMarkup)


def handle_user_api_modify_task(message, bot_wrapper: Bot):
    bot_info = bot_wrapper.bot_info
    bot = bot_wrapper.bot

    text = message.text
    block_idx = bot_info.tasks_view_info.block_idx
    block_count = bot_info.tasks_view_info.block_count

    if text == NEXT:
        bot_info.tasks_view_info.block_idx = (block_idx + 1) % block_count  # increment block idx
        bot.send_message(bot_info.chat_id, "next page", reply_markup=
        get_choose_task_markup(bot_info.tasks_view_info, bot_info.tasks_view_info.block_idx))

    elif text == PREV:
        bot_info.tasks_view_info.block_idx = (block_idx - 1) % block_count  # decrement block idx
        bot.send_message(bot_info.chat_id, "prev page", reply_markup=
        get_choose_task_markup(bot_info.tasks_view_info, bot_info.tasks_view_info.block_idx))

    elif text == DONE:
        bot_info.change_handler_info(Mode.USER, UserState.USE_API)
        bot.send_message(bot_info.chat_id, "choose command: ", reply_markup=chooseApiCommandMarkup)
    else:
        task_id = bot_info.tasks_view_info.get_task_id(text)    # get task id by text from clicked task button

        if task_id is None:
            bot.send_message(bot_info.chat_id, "choose suggested task", reply_markup=
            get_choose_task_markup(bot_info.tasks_view_info, bot_info.tasks_view_info.block_idx))
        else:
            task = bot_info.get_task(int(task_id))
            bot_info.chosen_task_view_markup = get_task_attributes_markup(dict(task))     # create task attributes view markup

            bot.send_message(bot_info.chat_id, "choose attribute to modify:",
                             reply_markup=bot_info.chosen_task_view_markup)
            # set id parameter
            bot_info.query_info.query_parameters[id] = task_id
            bot_info.set_state(UserState.MODIFY_TASK_PROCESS)

            bot_info.modifying_task = dict(task)


def handle_user_api_modify_task_process(message, bot_wrapper: Bot):
    bot = bot_wrapper.bot
    bot_info = bot_wrapper.bot_info

    # get modified attribute name
    text = message.text
    tokens = text.split(':')
    arg = tokens[0]

    # check is token represents an attribute name
    if arg == DONE:
        bot.send_message(bot_info.chat_id, "modifying task...")
        response = modify_task(bot_info.query_info.query_parameters)

        if response[STATUS] == FAIL:
            bot.send_message(bot_info.chat_id, "*API exception:* " + response[EXCEPTION], parse_mode="MARKDOWN")
            bot.send_message(bot_info.chat_id, "choose attribute to modify:",
                             reply_markup=bot_info.chosen_task_view_markup)
        else:
            bot_info.change_handler_info(Mode.USER, UserState.MODIFY_TASK)

            modifying_task = bot_info.modifying_task
            bot_info.reset_task(modifying_task[id], modifying_task)     # reset modified task

            bot.send_message(bot_info.chat_id, "task is successfully modified")
            first_block_idx = 0

            bot_info.tasks_view_info = TaskViewInfo(bot_info.tasks_list)    # update task view info
            bot.send_message(bot_info.chat_id, "choose task you want to modify:",
                             reply_markup=get_choose_task_markup(bot_info.tasks_view_info, first_block_idx))

    elif arg not in modify_task_attributes:
        bot.send_message(bot_info.chat_id, "choose suggested task attribute",
                         reply_markup=bot_info.chosen_task_view_markup)
    else:
        if arg == start_time_string_response:
            arg = start_time    # change this attribute on response attribute
        bot_info.query_info.cur_modifying_parameter = arg      # set current modified parameter
        bot_info.change_handler_info(Mode.USER, UserState.SET_ATTRIBUTE_VALUE)
        bot.send_message(bot_info.chat_id, "enter new value for the attribute - " + arg + ":")


def handle_user_api_set_attribute(message, bot_wrapper: Bot):
    bot = bot_wrapper.bot
    bot_info = bot_wrapper.bot_info
    text = message.text

    modifying_attribute = bot_info.query_info.cur_modifying_parameter

    bot_info.query_info.query_parameters[modifying_attribute] = text    # modify query info (need for back-end API call)
    bot_info.modifying_task[modifying_attribute] = text                 # modify current task view (need for markup)

    bot_info.change_handler_info(Mode.USER, UserState.MODIFY_TASK_PROCESS)
    bot.send_message(bot_info.chat_id, "new value of attribute: " + modifying_attribute + " is cached")

    # need to pass a COPY of the task:
    bot.send_message(bot_info.chat_id, "choose attribute to modify:",
                     reply_markup=get_task_attributes_markup(dict(bot_info.modifying_task)))


def handle_user_api_get_all_tasks(bot_wrapper: Bot):
    bot_info = bot_wrapper.bot_info
    bot = bot_wrapper.bot

    # print all tasks
    response = get_all_tasks()
    display_tasks(bot, bot_info.chat_id, response)
    bot.send_message(bot_info.chat_id, "choose command: ", reply_markup=chooseApiCommandMarkup)


def handle_user_api_create_task(message, bot_wrapper: Bot):
    bot_info = bot_wrapper.bot_info
    bot = bot_wrapper.bot

    text = message.text
    cur_parameter = bot_info.query_info.get_cur_parameter()

    if text != default_parameter_value:
        bot_info.query_info.query_parameters[cur_parameter] = text

    if bot_info.query_info.next_parameter() is None:  # check is the last parameter was initialized
        response = create_task(bot_info.query_info.query_parameters)  # send request

        if response[STATUS] == FAIL:
            bot.send_message(bot_info.chat_id, "*API exception:*\n" + response[EXCEPTION],
                             parse_mode="MARKDOWN", reply_markup=chooseApiCommandMarkup)
        else:
            bot.send_message(bot_info.chat_id, "*task created:*", parse_mode='MARKDOWN')
            display_task(bot, bot_info.chat_id, response[TASKS_LIST][0])
        bot_info.change_handler_info(Mode.USER, UserState.USE_API)
        bot.send_message(bot_info.chat_id, "choose command: ", reply_markup=chooseApiCommandMarkup)
    else:
        bot.send_message(bot_info.chat_id, "enter " + str(bot_info.query_info.get_cur_parameter()) + ":")


def handle_user_authentication(message, bot_wrapper: Bot):
    bot_info = bot_wrapper.bot_info
    bot = bot_wrapper.bot

    text = message.text
    tokens = text.split()
    tokens_count = len(tokens)

    if tokens_count != 2:
        bot.send_message(bot_info.chat_id, str(tokens_count) + " words got, should be 2 - 'username', 'password'")
        bot.send_message(bot_info.chat_id, login_message)
    else:
        username = tokens[0]
        password = tokens[1]
        user = bot_info.user_table.get_user(username)

        if user is None:
            bot.send_message(bot_info.chat_id, "user with name " + username + " doesn't exists")
            bot.send_message(bot_info.chat_id, login_message)
        else:
            if user.password != password:
                bot.send_message(bot_info.chat_id, "invalid password")
                bot.send_message(bot_info.chat_id, login_message)
            else:
                bot_info.change_handler_info(Mode.USER, UserState.CHOOSE_ACTION)
                bot.send_message(bot_info.chat_id, "authentication succeed", reply_markup=chooseUserActionMarkup)
