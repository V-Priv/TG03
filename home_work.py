import asyncio
import logging
import sqlite3
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import TOKEN

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

logging.basicConfig(level=logging.INFO)

# Создаем или подключаемся к базе данных
connection = sqlite3.connect('school_data.db')
cursor = connection.cursor()

# Создаем таблицу students
cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    grade TEXT NOT NULL
)
''')

# Сохраняем изменения и закрываем соединение
connection.commit()
connection.close()


# Определяем шаги состояния
class Form(StatesGroup):
    name = State()
    age = State()
    grade = State()


# Начало диалога
@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer("Введите ваше имя:")
    await state.set_state(Form.name)


# Ловим имя
@dp.message(Form.name)
async def name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите ваш возраст:")
    await state.set_state(Form.age)


# Ловим возраст
@dp.message(StateFilter(Form.age), F.text.func(lambda text: not text.isdigit()))
async def process_age_invalid(message: types.Message):
    return await message.answer("Возраст должен быть числом.\nВведите ваш возраст:")


@dp.message(StateFilter(Form.age), F.text.func(lambda text: text.isdigit()))
async def process_age(message: types.Message, state: FSMContext):
    await state.update_data(age=int(message.text))
    await state.set_state(Form.grade)
    await message.answer("Введите ваш класс:")


# Ловим класс
@dp.message(StateFilter(Form.grade))
async def process_grade(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    user_data['grade'] = message.text

    # Сохраняем данные в базу
    connection = sqlite3.connect('school_data.db')
    cursor = connection.cursor()
    cursor.execute('''
                        INSERT INTO students (name, age, grade) VALUES (?, ?, ?)
                    ''', (user_data['name'], user_data['age'], user_data['grade']))
    connection.commit()
    connection.close()

    await message.answer("Ваши данные сохранены!")
    await state.clear()


# Функция для запуска бота
async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
