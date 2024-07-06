import telebot
import requests
from config import TOKEN
from telebot import types
from main import get_area_id_by_name

bot = telebot.TeleBot(TOKEN)

bot.set_my_commands([
    telebot.types.BotCommand("start", "Начать поиск вакансий"),
    telebot.types.BotCommand("get_all", "Получить все вакансии из базы данных с сортировкой по зарплате")
])

user_data = {}

def create_main_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_search = types.KeyboardButton("Начать поиск вакансий с сайта hh.ru")
    button_search_in_db = types.KeyboardButton("Вакансии из базы данных")
    button_cancel = types.KeyboardButton("Отмена поиска")
    keyboard.add(button_search, button_search_in_db, button_cancel)
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
    experiences = {
        "Нет опыта": "Нет опыта",
        "От 1 года до 3 лет": "От 1 года до 3 лет",
        "От 3 до 6 лет": "От 3 до 6 лет",
        "Более 6 лет": "Более 6 лет"
    }
    for label, value in experiences.items():
        keyboard.add(types.InlineKeyboardButton(label, callback_data=f"experience_{value}"))
    return keyboard
def create_employment_menu():
    keyboard = types.InlineKeyboardMarkup()
    employments = {
        "Полная занятость": "Полная занятость",
        "Частичная занятость": "Частичная занятость",
        "Проектная работа": "Проектная работа",
        "Волонтерство": "Волонтерство",
        "Стажировка": "Стажировка"
                   }
    for label, value in employments.items():
        keyboard.add(types.InlineKeyboardButton(label, callback_data=f"employment_{value}"))
    return keyboard
@bot.message_handler(commands=['start'])
def start(message):
    keyboard = create_main_menu()
    bot.send_message(message.chat.id, "Привет! Я могу помочь вам найти вакансии. Выберите действие:", reply_markup=keyboard)
    user_data[message.chat.id] = {'state': 'START'}

@bot.message_handler(func=lambda message: message.text == "Отмена поиска")
def cancel_search(message):
    user_data.pop(message.chat.id, None)
    keyboard = create_main_menu()
    bot.send_message(message.chat.id, "Поиск отменен. Выберите действие:", reply_markup=keyboard)
    user_data[message.chat.id] = {'state': 'START'}

@bot.message_handler(func=lambda message: message.text == 'Вакансии из базы данных')
def ask_for_job_title(message):
    bot.send_message(message.chat.id, "Введите название вакансии для поиска.")
    user_data[message.chat.id]['state'] = 'WAITING_FOR_JOB_TITLE'

@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get('state') == 'WAITING_FOR_JOB_TITLE')
def show_vacancies_by_name(message):
    user_data[message.chat.id]['state'] = 'WAITING_FOR_SORT'
    profession = message.text
    user_data[message.chat.id]['profession'] = profession
    send_vacancies_db(message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('filter_'))
def handle_filter_choice(call):
    if call.data == 'filter_city':
        bot.send_message(call.message.chat.id, "Введите название города:")
        user_data[call.message.chat.id]['state'] = 'WAITING_FOR_CITY_DB'
    elif call.data == 'filter_experience':
        bot.send_message(call.message.chat.id, "Выберите опыт работы:", reply_markup=create_experience_menu())
        user_data[call.message.chat.id]['state'] = 'WAITING_FOR_EXPERIENCE_DB'
    elif call.data == 'filter_employment':
        bot.send_message(call.message.chat.id, "Выберите тип занятости:", reply_markup=create_employment_menu())
        user_data[call.message.chat.id]['state'] = 'WAITING_FOR_EMPLOYMENT_DB'

@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get('state') == 'WAITING_FOR_CITY_DB')
def handle_city_input(message):
    city_name = message.text
    user_data[message.chat.id]['city'] = city_name
    bot.send_message(message.chat.id, f"Вы выбрали город: {city_name}")
    send_vacancies_db(message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('experience_'))
def handle_experience_choice(call):
    experience = call.data.split('_')[1]
    user_data[call.message.chat.id]['experience'] = experience
    bot.send_message(call.message.chat.id, f"Вы выбрали опыт работы: {experience}")
    send_vacancies_db(call.message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('employment_'))
def handle_employment_choice(call):
    employment = call.data.split('_')[1]
    user_data[call.message.chat.id]['employment'] = employment
    bot.send_message(call.message.chat.id, f"Вы выбрали тип занятости: {employment}")
    send_vacancies_db(call.message.chat.id)


def send_vacancies_db(chat_id):
    data = user_data.get(chat_id, {})
    profession = data.get('profession')
    city = data.get('city')
    experience = data.get('experience')
    employment = data.get('employment')

    params = {"name": profession}
    if city:
        params["area"] = city
    if experience:
        params["experience"] = experience
    if employment:
        params["employment"] = employment

    response = requests.get(f"http://127.0.0.1:8000/vacancies/", params=params)
    if response.status_code == 200:
        vacancies = response.json()
        if vacancies:
            for vacancy in vacancies:
                bot.send_message(chat_id, f"{vacancy['name']} в {vacancy['employer']} ({vacancy['area']})\n"
                                          f"Зарплата: {vacancy['salary']}\n"
                                          f"Опыт работы: {vacancy['experience']}\n"
                                          f"Тип занятости: {vacancy['employment']}")
            bot.send_message(chat_id, "Выберите дальнейшие действия:", reply_markup=create_filter_menu())
        else:
            bot.send_message(chat_id, "Вакансий с таким названием не найдено.")

@bot.message_handler(func=lambda message: message.text == "Начать поиск вакансий с сайта hh.ru")
def handle_start_search(message):
        bot.send_message(message.chat.id, "Введите название города:")
        user_data[message.chat.id]['state'] = 'WAITING_FOR_CITY'


@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get('state') == 'WAITING_FOR_CITY')
def handle_city(message):
    area_id = get_area_id_by_name(message.text)
    if area_id:
        user_data[message.chat.id]['area'] = area_id
        user_data[message.chat.id]['state'] = 'WAITING_FOR_PROFESSION'
        bot.send_message(message.chat.id, 'Введите название профессии:')
    else:
        bot.send_message(message.chat.id, 'Город не найден, попробуйте еще раз:')

@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get('state') == 'WAITING_FOR_PROFESSION')
def handle_profession(message):
    user_data[message.chat.id]['profession'] = message.text
    user_data[message.chat.id]['state'] = 'WAITING_FOR_SALARY'
    bot.send_message(message.chat.id, 'Введите желаему заработную плату:')

@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get('state') == 'WAITING_FOR_SALARY')
def handle_salary(message):
    user_data[message.chat.id]['salary'] = message.text
    user_data[message.chat.id]['state'] = 'WAITING_FOR_EXPERIENCE'
    send_experience_buttons(message.chat.id)

def send_experience_buttons(chat_id):
    keyboard = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton(text="Без опыта", callback_data='noExperience'),
        types.InlineKeyboardButton(text="1-3 года", callback_data='between1And3'),
        types.InlineKeyboardButton(text="3-6 лет", callback_data='between3And6'),
        types.InlineKeyboardButton(text="Более 6 лет", callback_data='moreThan6')
    ]
    keyboard.add(*buttons)
    bot.send_message(chat_id, "Выберите опыт работы:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data in ['noExperience', 'between1And3', 'between3And6', 'moreThan6'])
def handle_experience(call):
    user_data[call.message.chat.id]['experience'] = call.data
    user_data[call.message.chat.id]['state'] = 'WAITING_FOR_EMPLOYMENT'
    send_employment_buttons(call.message.chat.id)

def send_employment_buttons(chat_id):
    keyboard = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton(text="Полная", callback_data='full'),
        types.InlineKeyboardButton(text="Частичная", callback_data='part'),
        types.InlineKeyboardButton(text="Проектная", callback_data='project'),
        types.InlineKeyboardButton(text="Волонтерство", callback_data='volunteer'),
        types.InlineKeyboardButton(text="Стажировка", callback_data='probation')
    ]
    keyboard.add(*buttons)
    bot.send_message(chat_id, "Выберите тип занятости:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data in ['full', 'part', 'project', 'volunteer', 'probation'])
def handle_employment(call):
    user_data[call.message.chat.id]['employment'] = call.data
    user_data[call.message.chat.id]['page'] = 0
    data = user_data[call.message.chat.id]
    send_vacancies(call.message.chat.id, data)

def send_vacancies(chat_id, data):
    profession = data.get('profession')
    area = data.get('area')
    salary = data.get('salary')
    experience = data.get('experience')
    employment = data.get('employment')
    page = data.get('page', 0)
    response = requests.get(f"http://127.0.0.1:8000//search/", params={"query": profession, "area": area, "salary": salary, "experience": experience, "employment": employment, "page": page})
    if response.status_code == 200:
        vacancies = response.json()
        if 'items' in vacancies:
            for vacancy in vacancies['items']:
                salary_info = vacancy.get('salary')
                salary_text = f"Salary: {salary_info['from']} - {salary_info['to']}" if salary_info else "Salary: Not specified"
                bot.send_message(
                    chat_id,
                    f"{vacancy['name']} в {vacancy['employer']['name']} ({vacancy['area']['name']})\n"
                    f"{salary_text}\n"
                    f"Опыт работы: {vacancy['experience']['name']}\n"
                    f"Тип занятости: {vacancy['employment']['name']}"
                )
        else:
            bot.send_message(chat_id, "Вакансий с таким названием не найдено.")

        #кнопки для перелистывания страниц
        keyboard = types.InlineKeyboardMarkup()
        next_button = types.InlineKeyboardButton("Следующая страница", callback_data='next_page')
        keyboard.add(next_button)
        bot.send_message(chat_id, "Показаны результаты страницы", reply_markup=keyboard)
    else:
        bot.send_message(chat_id, 'Вакансии закончились или произошла ошибка.')

@bot.callback_query_handler(func=lambda call: call.data == 'next_page')
def next_page(call):
    chat_id = call.message.chat.id
    if chat_id in user_data:
        user_data[chat_id]['page'] += 1
        send_vacancies(chat_id, user_data[chat_id])
    bot.answer_callback_query(call.id)

# Работа с бд
@bot.message_handler(commands=['get_all'])
def handle_vacancies(message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("По возрастанию зарплаты", callback_data="sort_asc"))
    keyboard.add(types.InlineKeyboardButton("По убыванию зарплаты", callback_data="sort_desc"))
    bot.send_message(message.chat.id, "Как отсортировать вакансии?", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data in ["sort_asc", "sort_desc"])
def callback_sort(call):
    order = "asc" if call.data == "sort_asc" else "desc"
    response = requests.get(f"http://127.0.0.1:8000/vacancies/search_by_salary/?sort_by=salary&order={order}")
    if response.status_code == 200:
        vacancies = response.json()
        if vacancies:
            for vacancy in vacancies:
                bot.send_message(call.message.chat.id, f"{vacancy['name']} в {vacancy['employer']} ({vacancy['area']})\n{vacancy['salary']}\n")
        else:
            bot.send_message(call.message.chat.id, "Нет вакансий по вашему запросу.")
    else:
        bot.send_message(call.message.chat.id, "Произошла ошибка при получении вакансий.")

if __name__ == '__main__':
    bot.remove_webhook()
    bot.polling(none_stop=True)
