import random

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

TOKEN = 'dbfd8cff45be33798ada6fdedd1672895b930e0fae2968f26d23024676029e59e7aa29e1a336115e7d90f'


class Bot:
    def __init__(self):
        pass

    def hello(self):
        message = random.choice(['Привет!', 'Здравствуй!', 'Хай', 'Доброго времени суток!'])
        return message

    def try_again(self):
        message = 'Извините, я не понял команду. Пожалуйста, проверьте, правильно ли вы её написали. Полный список ' \
                  'команд можно найти по команде "Помощь". '
        return message


def main():
    vk_session = vk_api.VkApi(token=TOKEN)
    longpoll = VkBotLongPoll(vk_session, 204058454)
    bot = Bot()
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            vk = vk_session.get_api()
            if event.obj.message['text'].lower() == 'привет' or event.obj.message['text'] == 'Начать':
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=bot.hello(),
                                 random_id=random.randint(0, 2 ** 64))
            else:
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=bot.try_again(),
                                 random_id=random.randint(0, 2 ** 64))


if __name__ == '__main__':
    main()
