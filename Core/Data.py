from enum import Enum

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
        self.max_id = 0

    def add_user(self, name: str, password: str):
        assert name is not None and password is not None

        user = User(name, password)
        self.max_id += 1
        self.users[self.max_id] = user

        return self.max_id

    def remove_user(self, user_id: int):
        if not (user_id in self.users):
            return False
        else:
            self.users.pop(user_id)
            if len(self.users) == 0:
                self.max_id = 0
            elif user_id == self.max_id:
                self.max_id = max(self.users.keys())
            return True

    def get_user(self, user_id):
        if not (user_id in self.users):
            return None
        else:
            return self.users[user_id]

    def refactor_user(self, user_id, name, password):
        if not (user_id in self.users):
            return False
        else:
            if name is not None:
                self.users[user_id].name = name
            if password is not None:
                self.users[user_id].password = password

            return True

    def get_user_by_name(self, name):
        for key in self.users:
            if self.users[key].name == name:
                return key
        return -1

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
    descr = task[description][:char_count]

    return str(task[id]) + "\n" + descr


class TaskViewInfo:
    def __init__(self, tasks: list):
        self.block_size = 4         # count of tasks on screen
        self.tasks_info = []

        block_idx = -1

        for i in range(len(tasks)):
            task = tasks[i]

            if i % self.block_size == 0:
                block_idx += 1
                self.tasks_info.append(set())
            self.tasks_info[block_idx].add(get_task_info_text(task))

        self.block_count = len(self.tasks_info)
        self.block_idx = 0

    def get_task_id(self, text):
        for block in self.tasks_info:
            if text in block:
                return text.split()[0]
        return None
