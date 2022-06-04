import sys
from Tools.config import load_config_to_bot, save_default_config
from Core.Bot import Bot
from Web.api_requests import create_task

if __name__ == '__main__':
    args = sys.argv

    if len(args) != 3:
        print("fatal: invalid command line arguments count")
        exit(1)
    telegram_api_token = args[1]
    reset_config = args[2]

    if reset_config == 'True':
        save_default_config()
        print("config saved")
    elif reset_config == 'False':
        pass
    else:
        print("fatal: invalid command line argument")
        exit(1)
    BotInstance = Bot(telegram_api_token)
    load_config_to_bot(BotInstance.bot_info)
    BotInstance.bot.infinity_polling()
