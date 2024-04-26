import os 
from faker import Faker
from random import randint
from sqlalchemy import create_engine, Column, Integer, String, func
from sqlalchemy.orm import sessionmaker, declarative_base
from random import randint
import pandas as pd

Base = declarative_base()


class Word(Base):
    __tablename__ = 'words'
    id = Column(Integer, primary_key=True)
    word = Column(String(5), unique=False)

    @staticmethod
    def get_random_word(session):
        total_words = session.query(func.count(Word.id)).scalar()
        random_index = randint(0, total_words - 1)
        return session.query(Word.word).offset(random_index).limit(1).scalar()

engine = create_engine('sqlite:///wordle.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

script_dir = os.path.dirname(__file__)
csv_path = os.path.join(script_dir, 'words.csv')
df = pd.read_csv(csv_path)

for word in df["word"]:
    word = Word(word=word)
    session.add(word)
session.commit()