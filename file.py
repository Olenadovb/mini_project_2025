from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///./test.db")  # заміни шлях, якщо інший

with engine.connect() as conn:
    conn.execute(text("DELETE FROM alembic_version"))
    conn.commit()
