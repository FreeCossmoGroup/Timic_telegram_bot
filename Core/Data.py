from enum import Enum


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
