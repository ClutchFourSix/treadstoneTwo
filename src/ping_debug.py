import os
from output.telegram_bot_v3 import TelegramBotV3


def mask(value):
    if value is None:
        return 'None'
    s = str(value)
    if len(s) <= 4:
        return s
    return f"{s[:2]}***{s[-2:]}"


def main():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    print('DEBUG TOKEN PRESENT:', token is not None)
    print('DEBUG CHAT_ID RAW REPR:', repr(chat_id))
    print('DEBUG CHAT_ID MASKED:', mask(chat_id))
    TelegramBotV3().send('PING DEBUG OK')


if __name__ == '__main__':
    main()
