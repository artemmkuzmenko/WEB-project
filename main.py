import datetime
import random

import requests
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

TOKEN = 'dbfd8cff45be33798ada6fdedd1672895b930e0fae2968f26d23024676029e59e7aa29e1a336115e7d90f'


# код API, позволяющий боту писать сообщения от имени сообщества


class Bot:
    # класс бота, здесь представлены все его ответы на сообщения
    def __init__(self):
        pass

    def hello(self):
        # бот случайным образом выбирает приветственное сообщение
        message = random.choice(['Привет!', 'Здравствуй!', 'Хай', 'Доброго времени суток!'])
        return message

    def try_again(self):
        # бот не понял команду
        message = 'Извините, я не понял команду. Пожалуйста, проверьте, правильно ли вы её написали. Полный список ' \
                  'команд можно найти по команде "Помощь".'
        return message

    def goodbye(self):
        # бот случайным образом выбирает сообщение, чтобы попрощаться с пользователем
        message = random.choice(['Пока!', 'Заходи ещё!', 'Удачи!', 'До скорого!'])
        return message

    def get_time(self):
        # бот сообщает пользователю точное время для его часового пояса
        message = datetime.datetime.now()
        return message

    def get_coordinates(self, place):
        # бот определяет координаты места по заданному адресу, используя открытый API Яндекс.Карт
        geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode=" \
                           f"{place}&format=json"
        response = requests.get(geocoder_request)
        json_response = response.json()
        coordinates = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
        return coordinates

    def get_address(self, coordinates):
        # метод, обратный предыдущему, то есть определение адреса по координатам
        geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode=" \
                           f"{coordinates}&format=json"
        response = requests.get(geocoder_request)
        json_response = response.json()
        address = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"] \
            ["metaDataProperty"]["GeocoderMetaData"]["text"]
        return address

    def help(self):
        # получение справки по всем командам бота
        message = """Все команды можно вводить в любом регистре. Список команд:\nПривет - чтобы поздороваться с ботом
        . Пока - чтобы с ним попрощаться. Время - вы узнаете точное время. Координаты <адрес> - узнать координаты опреде
        лённого места. Адрес <координаты> - узнать адрес по координатам."""
        return message

    def get_weather(self):
        response = requests.get("""http://api.openweathermap.org/data/2.5/find?q=Moscow&type=like&APPID=2300ca5dfdf70c9f
        4bd299061a3e0ae8""")
        json_response = response.json()
        message = ' '.join(["conditions:", json_response['weather'][0]['description'], "temp:", json_response['main'] \
            ['temp'], "temp_min:", json_response['main']['temp_min'], "temp_max:", json_response['main']['temp_max']])
        return message


def main():
    # получение API сообщества по ключу
    vk_session = vk_api.VkApi(token=TOKEN)
    print('Сессия началась')
    # подключение к сообщениям сообщества
    longpoll = VkBotLongPoll(vk_session, 204058454)
    print('Есть подключение')
    # создание бота
    bot = Bot()
    print('Бот активирован')
    # бесконечный цикл обработки сообщений
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            vk = vk_session.get_api()
            text = event.obj.message['text']
            # далее идёт обработка возможных сообщений с вызовом соответствующих методов бота
            # в конце обработка других сообщений, на кторые бот должен ответить, что он не понял
            if text.lower() == 'привет' or text == 'Начать':
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=bot.hello(),
                                 random_id=random.randint(0, 2 ** 64))
            elif text.lower() == 'пока':
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=bot.goodbye(),
                                 random_id=random.randint(0, 2 ** 64))
            elif text.lower() == 'время':
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=bot.get_time(),
                                 random_id=random.randint(0, 2 ** 64))
            elif 'координаты' in text.lower():
                toponym = ' '.join(text.split()[1:])
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=bot.get_coordinates(toponym),
                                 random_id=random.randint(0, 2 ** 64))
            elif 'адрес' in text.lower():
                coordinates = ' '.join(text.split()[1:])
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=bot.get_address(coordinates),
                                 random_id=random.randint(0, 2 ** 64))
            elif text.lower() == 'Помощь':
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=bot.help(),
                                 random_id=random.randint(0, 2 ** 64))
            else:
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=bot.try_again(),
                                 random_id=random.randint(0, 2 ** 64))


if __name__ == '__main__':
    main()
