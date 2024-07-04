import telebot
from config import TOKEN
from telebot import types
from main import search_vacancies, get_area_id_by_name


bot = telebot.TeleBot(TOKEN)

bot.set_my_commands([
    telebot.types.BotCommand("start", "Начать работу с ботом")
])

user_data = {}

def create_main_menu():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_search = types.KeyboardButton("Начать поиск вакансий")
    button_cancel = types.KeyboardButton("Отмена поиска")
    keyboard.add(button_search, button_cancel)
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

@bot.message_handler(func=lambda message: message.text == "Начать поиск вакансий")
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

    vacancies = search_vacancies(profession, area=area, salary=salary, experience=experience, employment=employment, page=page)
    if 'items' in vacancies and vacancies['items']:
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

if __name__ == '__main__':
    bot.remove_webhook()
    bot.polling(none_stop=True)
