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
        лённого места. Адрес <координаты> - узнать адрес по координатам. Погода [город] - узнать текущую погоду в 
        городе (название надо вводить по-английски, если не ввести никакое название будет дана погода для Москвы)."""
        return message

    def get_weather(self, city='Moscow,RU'):
        # метод, для полуучения погоды в определённом месте
        appid = '2300ca5dfdf70c9f4bd299061a3e0ae8'
        res = requests.get("http://api.openweathermap.org/data/2.5/find",
                           params={'q': city, 'type': 'like', 'units': 'metric', 'APPID': appid})
        json_res = res.json()
        city_id = json_res['list'][0]['id']
        # сначала определяется идентификатор города
        response = requests.get("http://api.openweathermap.org/data/2.5/weather",
                                params={'id': city_id, 'units': 'metric', 'lang': 'ru', 'APPID': appid})
        json_response = response.json()
        # теперь получена информация о погоде
        message = 'Условия: ' + json_response['weather'][0]['description'] + '\n'
        message += 'Температура: ' + json_response['main']['temp'] + '\n'
        message += 'Температура по ощущению: ' + json_response['main']['feels_like'] + '\n'
        message += 'Минимальная температура: ' + json_response['main']['temp_max'] + '\n'
        message += 'Максимальная температура: ' + json_response['main']['temp_min'] + '\n'
        message += 'Давление: ' + json_response['main']['pressure'] + '\n'
        message += 'Скорость ветра' + json_response['wind']['speed'] + '\n'
        message += 'Направление ветра' + json_response['wind']['deg']
        # из полученной информации составляется сообщение
        return message



def main():
    # получение API сообщества по ключу
    vk_session = vk_api.VkApi(token=TOKEN)
    # подключение к сообщениям сообщества
    longpoll = VkBotLongPoll(vk_session, 204058454)
    # создание бота
    bot = Bot()
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
            elif text.lower() == 'помощь':
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=bot.help(),
                                 random_id=random.randint(0, 2 ** 64))
            elif text.lower() == 'погода':
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=bot.get_weather(),
                                 random_id=random.randint(0, 2 ** 64))
            elif 'погода' in text.lower():
                city = text.split()[1]
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=bot.get_weather(city=city),
                                 random_id=random.randint(0, 2 ** 64))
            else:
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=bot.try_again(),
                                 random_id=random.randint(0, 2 ** 64))


if __name__ == '__main__':
    main()
