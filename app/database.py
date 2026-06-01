from sqlalchemy import create_engine
from sqlalchem.orm import sessionmaker

DATABASE_URL = "postgresql://pabellon:pabellon123@localhost:5432/pabellon_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()

