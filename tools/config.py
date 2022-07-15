import pickle
from pathlib import Path

from core.date import UserTable, BotInfo

config_file_path = Path("resources/config.pickle")


def save_config(user_table: UserTable, admin_key: str):
    config = dict({"user_table": user_table, "admin_key": admin_key})
    pickle.dump(config, open(config_file_path, 'wb'))


def read_config():
    return pickle.load(open(config_file_path, 'rb'))


def save_default_config():
    save_config(UserTable(), "admin_key")


def load_config_to_bot(bot_info: BotInfo):
    config = read_config()
    bot_info.set_admin_key(config["admin_key"])
    bot_info.set_user_table(config["user_table"])


def save_config_from_bot(bot_info: BotInfo):
    save_config(bot_info.user_table, bot_info.admin_key)
