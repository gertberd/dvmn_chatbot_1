# Бот для оповещения о проверке работ
Бот отправляет оповещения о проверке работ на курсах [dvmn.org](https://dvmn.org/).

### Как установить
Необходимо:
1. Создать бота в Telegram - [@BotFather](https://telegram.me/BotFather) и получить его токен
2. Узнать chat_id - написать @userinfobot
3. Получить токен API dmnv.org - [Документация API](https://dvmn.org/api/docs/)
4. Внести все данные в файл ```.env``` в корне проекта в таком виде:
```
DVMN_API_TOKEN=asd32y52475h9824ht3984t2
BOT_TOKEN=95132391:wP3db3301vnrob33BZdb33KwP3db3F1I
CHAT_ID=1234567
```
Python3 должен быть уже установлен. 
Затем используйте `pip` (или `pip3`, есть есть конфликт с Python2) для установки зависимостей:
```
pip install -r requirements.txt
```
Для запуска бота запустите main.py.
```
python main.py
```

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).
