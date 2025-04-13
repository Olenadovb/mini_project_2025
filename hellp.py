from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table, MetaData

# Підключення до бази даних
engine = create_engine(
    "sqlite:///test.db"
)  # Заміни на правильний URL до твоєї бази даних
Session = sessionmaker(bind=engine)
session = Session()

# Використовуємо інспектора для перевірки наявності таблиці
inspector = inspect(engine)

# Перевіряємо наявність таблиці 'Users'
if "Users" in inspector.get_table_names():
    print("Таблиця 'Users' існує!")

    # Отримуємо всі дані з таблиці 'Users'
    metadata = MetaData()
    users_table = Table("Users", metadata, autoload_with=engine)

    # Отримуємо всі записи з таблиці
    result = session.execute(users_table.select()).fetchall()

    # Виводимо результат
    print(f"Дані з таблиці 'Users':")
    for row in result:
        print(row)
else:
    print("Таблиця 'Users' не знайдена.")
