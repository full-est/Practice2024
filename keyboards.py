from telebot import types

def create_main_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Начать поиск вакансий с сайта hh.ru"))
    keyboard.add(types.KeyboardButton("Вакансии из базы данных"))
    keyboard.add(types.KeyboardButton("Отмена поиска"))
    return keyboard

def create_filter_menu():
    keyboard = types.InlineKeyboardMarkup()
    button_city = types.InlineKeyboardButton("Фильтр по городу", callback_data="filter_city")
    button_experience = types.InlineKeyboardButton("Фильтр по опыту", callback_data="filter_experience")
    button_employment = types.InlineKeyboardButton("Фильтр по типу занятости", callback_data="filter_employment")
    keyboard.add(button_city, button_experience, button_employment)
    return keyboard

def create_experience_menu():
    keyboard = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton(text="Без опыта", callback_data='noExperience'),
        types.InlineKeyboardButton(text="1-3 года", callback_data='between1And3'),
        types.InlineKeyboardButton(text="3-6 лет", callback_data='between3And6'),
        types.InlineKeyboardButton(text="Более 6 лет", callback_data='moreThan6')
    ]
    keyboard.add(*buttons)
    return keyboard

def create_employment_menu():
    keyboard = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton(text="Полная", callback_data='full'),
        types.InlineKeyboardButton(text="Частичная", callback_data='part'),
        types.InlineKeyboardButton(text="Проектная", callback_data='project'),
        types.InlineKeyboardButton(text="Волонтерство", callback_data='volunteer'),
        types.InlineKeyboardButton(text="Стажировка", callback_data='probation')
    ]
    keyboard.add(*buttons)
    return keyboard