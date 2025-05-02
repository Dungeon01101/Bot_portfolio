from random import randint
import requests
import telebot
from telebot import types  # Import types for ReplyKeyboardMarkup
import sqlite3
import json

# Замените на свой токен
BOT_TOKEN = "7957132535:AAGOY_I2KEBXTSL_6fPN4DCqQtXeoRjFKBI"
bot = telebot.TeleBot(BOT_TOKEN)

# Пример данных и настроек
DATABASE = 'your_database.db'  # Replace with your database file
cancel_button = "Отмена ❌"

# Replace with your DB_Manager class (not shown here, assuming it exists)
# Example implementation needed for full functionality.

attributes_of_projects = {
    "Название 📝": ["Введи новое название проекта:", "project_name"],
    "Описание ℹ️": ["Введи новое описание проекта:", "description"],
    "Статус 🚦": ["Выбери новый статус проекта:", "status_id"]
}


def gen_markup(items, one_time_keyboard=True):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=one_time_keyboard)
    items.append(cancel_button)
    for item in items:
        markup.add(item)
    return markup

def cansel(message):
    bot.send_message(message.chat.id, "Действие отменено.")

def update_project_step_2(message, projects):
    project_name = message.text
    if message.text == cancel_button:
        cansel(message)
        return
    if project_name not in projects:
        bot.send_message(message.chat.id, "Что-то пошло не так! ⚠️ Выбери проект, который хочешь изменить еще раз:", reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, update_project_step_2, projects=projects)
        return
    bot.send_message(message.chat.id, "Выбери, что требуется изменить в проекте:", reply_markup=gen_markup(attributes_of_projects.keys()))
    bot.register_next_step_handler(message, update_project_step_3, project_name=project_name)

def update_project_step_3(message, project_name):
    attribute = message.text
    reply_markup = None
    if message.text == cancel_button:
        cansel(message)
        return
    if attribute not in attributes_of_projects.keys():
        bot.send_message(message.chat.id, "Кажется, ты ошибся, попробуй еще раз! 😕", reply_markup=gen_markup(attributes_of_projects.keys()))
        bot.register_next_step_handler(message, update_project_step_3, project_name=project_name)
        return
    elif attribute == "Статус 🚦":
        rows = manager.get_statuses()
        reply_markup=gen_markup([x[0] for x in rows])
    bot.send_message(message.chat.id, attributes_of_projects[attribute][0], reply_markup = reply_markup)
    bot.register_next_step_handler(message, update_project_step_4, project_name=project_name, attribute=attributes_of_projects[attribute][1])

def update_project_step_4(message, project_name, attribute):
    update_info = message.text
    if attribute== "status_id":
        rows = manager.get_statuses()
        if update_info in [x[0] for x in rows]:
            update_info = manager.get_status_id(update_info)
        elif update_info == cancel_button:
            cansel(message)
        else:
            bot.send_message(message.chat.id, "Был выбран неверный статус, попробуй еще раз! ⚠️", reply_markup=gen_markup([x[0] for x in rows]))
            bot.register_next_step_handler(message, update_project_step_4, project_name=project_name, attribute=attribute)
            return
    user_id = message.from_user.id
    data = (update_info, project_name, user_id)
    manager.update_projects(attribute, data)
    bot.send_message(message.chat.id, "Готово! ✅ Обновления внесены! 🎉", reply_markup=types.ReplyKeyboardRemove()) # Hide keyboard after update


def info_project(message, user_id, project):
    # Get project details from the database (assuming manager.get_project_details exists)
    project_details = manager.get_project_details(project, user_id)

    if project_details:
        project_name, description, status = project_details  # Adjust according to your database

        # Fetch status description from ID (assuming manager.get_status_description exists)
        status_description = manager.get_status_description(status)

        # Format project details nicely
        project_info = f"<b>{project_name}</b>\n\n"  # Bold project name
        project_info += f"Описание: {description}\n"
        project_info += f"Статус: {status_description}\n" # Show status description

        bot.send_message(message.chat.id, project_info, parse_mode='HTML')  # Use HTML for bold text

    else:
        bot.send_message(message.chat.id, "Не удалось получить информацию о проекте.")

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет!👋 Этот бот поможет тебе управлять проектами. Используй /info для просмотра доступных команд.")

@bot.message_handler(commands=['help', 'info'])
def info(message):
    help_text = """
    Список доступных команд:
    /start - Начать работу с ботом 👋
    /help - Получить список команд и их описание ℹ️
    /add_project - Добавить новый проект ➕
    /update_project - Обновить существующий проект 🔄
    [Название проекта] - Получить информацию о конкретном проекте 📝 (напишите название проекта текстом)
    """
    bot.send_message(message.chat.id, help_text)


@bot.message_handler(func=lambda message: True)
def text_handler(message):
    user_id = message.from_user.id
    projects =[ x[2] for x in manager.get_projects(user_id)]
    project = message.text
    if project in projects:
        info_project(message, user_id, project)
        return
    bot.reply_to(message, "Тебе нужна помощь? 🤔 Используй /help для просмотра доступных команд.") # more friendly message with emoji

if __name__ == '__main__':
    # Create dummy DB_Manager (replace with your actual class)
    class DummyDB_Manager:
        def __init__(self, db):
            self.db = db

        def get_projects(self, user_id):
            # Replace with actual database query
            return [("Project 1", "Description 1", "Project A"),
                    ("Project 2", "Description 2", "Project B")]

        def get_project_details(self, project, user_id):
            # Replace with database query
            if project == "Project A":
                return ("Project A", "This is project A", "To Do") # project_name, description, status_id
            elif project == "Project B":
                return ("Project B", "Another project", "In Progress")
            return None

        def get_statuses(self):
            # Replace with query
            return [("To Do",), ("In Progress",), ("Done",)]

        def get_status_id(self, status):
            # replace with query
            if status == "To Do": return "1"
            elif status == "In Progress": return "2"
            elif status == "Done": return "3"
            return None

        def get_status_description(self, status_id):
             # Replace with query to get description based on status ID
            if status_id == "1": return "To Do"
            elif status_id == "2": return "In Progress"
            elif status_id == "3": return "Done"
            return "Unknown"


        def update_projects(self, attribute, data):
            print(f"Updating {attribute} with {data}") # replace with actual db update

    manager = DummyDB_Manager(DATABASE)
    bot.infinity_polling()
