"""Constants and dictionaries of messages to be sent to user."""

EN = "en"
UA = "ua"
RU = "ru"
ENG = "English"
UKR = "Українська"
RUS = "Русский"
dialogs = {
    "ua": {
        "start": "Привіт! Я робот та можу допомогти тобі знайти твої іграшки.\nНапиши своє ім'я.",
        "ask_name": "Як тебе звати?",
        "ask_pet_name": ", тепер напиши мені им'я твоєї іграшки чи вихованця.",
        "wrong_name": "В імені не повинно бути цифр. Спробуй ще раз.",
        "search": "Шукаю, зачекай трохи...",
        "found": ", знайшов! Ось, лист для тебе.",
        "personal": "Будь ласка, не плачь і не хвилюйся.\n"
        "Я подорожую, хочу подивитися світ.\n"
        "Буду тобі писати про свої пригоди.\n"
        "А коли зустрінемося, розкажеш мені все цікаве.",
        "busy": "Привіт! Я зараз в одному цікавому місці, напишу тобі пізніше. Як справи, чим займаєшся?",
        "no_articles": "В мене немає для тебе новин. Напиши мені як твої справи.",
        "out_of_service": "Робот втомився і спить :-( \nСпробуй пізніше.",
        "unknown_command": "Я тебе не розумію.",
    },
    "ru": {
        "start": "Привет! Я робот и могу помочь тебе найти твои игрушки.\nНапиши как тебя зовут.",
        "wrong_name": "В имени не должно быть цифр. Попробуй еще раз.",
        "ask_name": "Как тебя зовут?",
        "ask_pet_name": ", теперь напиши мне имя твоей игрушки или питомца.",
        "search": "Ищу, подожди немного...",
        "found": ", нашел! Вот, письмо для тебя.",
        "personal": "Пожалуйста, не плачь и не волнуйся.\n"
        "Я путешествую, хочу посмотреть мир.\n"
        "Буду тебе писать о своих приключениях.\n"
        "А когда встретимся, расскажешь мне все интересное.",
        "busy": "Привет! Я сейчас в очень интересном месте, напишу тебе позже. Как у тебя дела, чем занимаешься?",
        "no_articles": "У меня пока нет для тебя новостей. Напиши мне как твои дела.",
        "out_of_service": "Робот устал и спит :-( \nПопробуй позже.",
        "unknown_command": "Я тебя не понимаю. Напиши по другому.",
    },
    "en": {
        "start": "Hi! I'm a robot and I'll help you to find your toys.\nWhat is your name?",
        "intro": "Hello! I can speak English, Ukrainian and Russian languages.",
        "choose_lang": "Please, choose your language using buttons below.",
        "wrong_name": "Name must not contain digits. Try again.",
        "ask_name": "What is your name?",
        "ask_pet_name": ", write me your toy's or pet's name.",
        "search": "Searching, wait a while...",
        "found": ", I've found! Here is a letter for you.",
        "personal": "Please don't cry and don't worry.\n"
        "I'm traveling now, I want to see the world.\n"
        "I'll write to you about my adventures.\n"
        "And when you meet me, you can tell me all the interesting things.",
        "busy": "Hi! I'm in a very interesting place now, I'll text to you later. How are you doing?",
        "no_articles": "I have no any news for you yet. Write me how are you doing.",
        "out_of_service": "Bot is sleeping now :-( \nTry again later.",
        "unknown_command": "I don't understand you.",
    },
}
