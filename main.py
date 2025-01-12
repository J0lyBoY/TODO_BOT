from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import os
import sqlite3
import asyncio
import logging


logging.basicConfig(
    level=logging.INFO,  # Уровень логирования
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Формат сообщений
    datefmt="%Y-%m-%d %H:%M:%S",  # Формат времени
    filename="app.log",  # Имя файла для записи логов
    filemode="w"  # Режим записи (a - добавление, w - перезапись)
)

con = sqlite3.connect('TODO.db')
cur = con.cursor()
cur.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                task TEXT
                )
""")
    


def get_task(user_id):
    cur.execute('SELECT id, task FROM tasks WHERE user_id = ?', (user_id,))
    tasks = cur.fetchall()
    return tasks

def del_task(task_id):
    cur.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    con.commit()


load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_command(message: Message):
    await message.reply("Привет! Я TODO бот. Вот список команд:\n/add <задача> - добавить задачу\n/list - показать список задач\n/delete <id> - удалить задачу по ID")

@dp.message(Command("add"))
async def add_task(message: types.Message):
    task = message.text.removeprefix('/add').strip()
    if not task:
        await message.reply("Пожалуйста укажите задачу после команды /add")
        return
    cur.execute("INSERT INTO tasks (user_id, task) VALUES (?, ?)", (message.from_user.id, task))
    con.commit()
    await message.answer('Задача добавлена')

@dp.message(Command("list"))
async def see_tasks(message: types.Message):
    cur.execute('SELECT id, task FROM tasks WHERE user_id = ?', (message.from_user.id,))
    tasks = cur.fetchall()
    if not tasks:
        await message.reply("У вас нет задач")
        return
    response = "Ваши задачи: \n"
    for task_id, task in tasks:
        response += f'{task_id}, {task} \n'
    await message.answer(response)

@dp.message(Command("delete"))
async def del_task(message: types.Message):
    task_id = int(message.text.removeprefix("/delete ").strip())
    cur.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    con.commit()
    await message.reply(f"Задача с ID {task_id} удалена.")
    

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())