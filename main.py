from tools.config import load_config_to_bot, save_default_config
from core.bot import Bot
import argparse

if __name__ == '__main__':
    def get_bool(string):
        if string == 'True':
            return True
        if string == 'False':
            return False
        else:
            raise ValueError() # will be handled in parse_args() method

    parser = argparse.ArgumentParser()
    parser.add_argument('token', help="your telegram API token")
    parser.add_argument('reset_config', type=get_bool, help="need to reset config to default or not")
    args = parser.parse_args()

    if args.reset_config:
        save_default_config()
        print("config is set to default")

    BotInstance = Bot(args.token)
    load_config_to_bot(BotInstance.bot_info)
    BotInstance.bot.infinity_polling()
