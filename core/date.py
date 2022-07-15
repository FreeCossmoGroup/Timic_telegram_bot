from enum import Enum
import re

server_address = "http://localhost:8080"

description = 'description'
start_time = 'stime'
duration = 'duration'
fixed = 'fixed'
parent = 'parent'
id = 'id'

default_parameter_value = '-'
create_task_body = {description: '', start_time: '', duration: '', fixed: '', parent: ''}
modify_task_body = {id: '', description: '', start_time: '', duration: '', fixed: '', parent: ''}

task_id_offset = 1
task_dscr_re = ':|\s'


class Mode(Enum):
    USER = 1
    ADMIN = 2
    LOGIN = 3


class UserState(Enum):
    CHANGE_USER_SETTINGS = 1
    LOGOUT = 2
    USE_API = 3
    AUTHENTICATION = 4
    CHOOSE_ACTION = 5
    CREATE_TASK = 6
    MODIFY_TASK = 7
    MODIFY_TASK_PROCESS = 8


class QueryType(Enum):
    CREATE_TASK = 1
    MODIFY_TASK = 2
    GET_ALL_TASKS = 3


class AdminState(Enum):
    RESET_KEY = 1
    ADD_USER = 2
    REMOVE_USER = 3
    AUTHENTICATION = 4
    CHOOSE_ACTION = 5


class User(object):
    def __init__(self, name, password):
        self.name = name
        self.password = password


class UserTable(object):
    def __init__(self):
        self.users = dict()

    def add_user(self, name: str, password: str):
        assert name is not None and password is not None

        if name in self.users:
            return False
        user = User(name, password)
        self.users[name] = user

        return True

    def remove_user(self, name):
        if name not in self.users:
            return False
        else:
            self.users.pop(name)

            return True

    def get_user(self, name):
        if name not in self.users:
            return None
        else:
            return self.users[name]

    def refactor_user(self, old_name, new_name, password):
        if old_name not in self.users or (new_name is None and password is None):
            return False
        else:
            user_id = old_name

            if new_name is not None:
                user = self.users.pop(old_name)
                user.name = new_name
                self.users[new_name] = user
                user_id = new_name

            if password is not None:
                self.users[user_id].password = password

            return True

    def get_size(self):
        return len(self.users)


class BotInfo(object):
    def __init__(self):
        self.is_started = False
        self.chat_id = -1
        self.mode = Mode.LOGIN
        self.state = None
        self.user_table = None
        self.admin_key = None

        # cached info:
        self.query_info = None
        self.tasks_view_info = None
        self.choose_task_info = None
        self.tasks_list = None

    def set_state(self, state):
        self.state = state

    def set_chat_id(self, id):
        self.chat_id = id

    def change_handler_info(self, mode, state):
        assert (mode == Mode.USER and type(state) is UserState) or \
               (mode == Mode.ADMIN and type(state) is AdminState) or \
               (mode == Mode.LOGIN and state is None)
        self.state = state
        self.mode = mode

    def set_user_table(self, user_table: UserTable):
        self.user_table = user_table

    def set_admin_key(self, admin_key: str):
        self.admin_key = admin_key

    def get_task(self, task_id):
        for task in self.tasks_list:
            if task[id] == task_id:
                return task
        return None


def get_create_task_parameters():
    return dict(create_task_body)


def get_modify_task_parameters():
    return dict(modify_task_body)


def get_task_parameters(type: QueryType):
    if type == QueryType.CREATE_TASK:
        return get_create_task_parameters()
    elif type == QueryType.MODIFY_TASK:
        return get_modify_task_parameters()


class QueryInfo:
    def __init__(self, type: QueryType):
        self.query_type = type

        if type == QueryType.CREATE_TASK or type == QueryType.MODIFY_TASK:
            self.query_parameters = get_task_parameters(type)
            self.parameter_count = len(self.query_parameters)
            self.cur_parameter_idx = 0

    def next_parameter(self):
        self.cur_parameter_idx += 1

        if self.cur_parameter_idx >= self.parameter_count:  # it was last parameter
            return None
        return self.cur_parameter_idx

    def get_cur_parameter(self):
        return list(self.query_parameters.keys())[self.cur_parameter_idx]


def get_task_info_text(task):
    char_count = 10
    dscr = task[description][:char_count]

    return "Task " + str(task[id]) + ": '" + dscr + "..'"


class TaskViewInfo:
    def __init__(self, tasks: list):
        self.block_size = 4         # count of tasks on screen
        self.tasks_info = []

        block_idx = -1

        for i in range(len(tasks)):
            task = tasks[i]

            if i % self.block_size == 0:
                block_idx += 1
                self.tasks_info.append(list())
            self.tasks_info[block_idx].append(get_task_info_text(task))

        self.block_count = len(self.tasks_info)
        self.block_idx = 0

    def get_task_id(self, text):
        for block in self.tasks_info:
            if text in block:
                return re.split(task_dscr_re, text)[task_id_offset]
        return None
