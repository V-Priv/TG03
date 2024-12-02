import sqlite3

# Подключаемся к базе данных
connection = sqlite3.connect('school_data.db')
cursor = connection.cursor()

# Выполняем запрос для получения всех данных из таблицы students
cursor.execute('SELECT * FROM students')

# Получаем все строки результата
rows = cursor.fetchall()

# Выводим данные
for row in rows:
    print(row)

# Закрываем соединение
connection.close()