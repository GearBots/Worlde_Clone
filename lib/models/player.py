#!/usr/bin/env python3
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import Session, declarative_base, validates, relationship


Base = declarative_base()

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True)
    name = Column(String(), unique=True)
    high_scores = relationship("HighScore", back_populates="player")

    def record_high_score(self, score):
        new_high_score = HighScore(score=score, player_id=self.id)
        self.high_scores.append(new_high_score)

class HighScore(Base):
    __tablename__ = "high_scores"

    id = Column(Integer, primary_key=True)
    score = Column(Integer())
    player_id = Column(Integer(), ForeignKey("players.id"))
    player = relationship("Player", back_populates="high_scores")

# class Word(Base):
#     __tablename__ = "words"

#     id = Column(Integer, primary_key=True)
#     word = Column(String("Apple"))

class Wordle:
    MAX_ATTEMPTS = 6
    WORD_LENGTH = 5

    def __init__(self, secret: str):
        self.secret: str = secret.upper()
        self.attempts = []
        pass

    def attempt(self, word: str):
        word = word.upper()
        self.attempts.append(word)

    def guesses(self, guess): 
        guess = guess.upper()
        results = []
        for i in range(self.WORD_LENGTH):
            character = guess[i]
            letter = LetterLogic(character)
            letter.in_word = character in self.secret
            letter.in_position = character == self.secret[i]
            results.append(letter)
        return results 

    @property
    def won_game(self):
        return len(self.attempts) > 0 and self.attempts[-1] == self.secret
    
    @property
    def attempts_left(self) -> int:
        return self.MAX_ATTEMPTS - len(self.attempts)
    @property
    def playing_game(self):
        return self.attempts_left > 0 and not self.won_game
    
class LetterLogic:
    def  __init__(self, character: str):
        self.character: str = character
        self.in_word: bool = False
        self.in_position: bool = False

    def __repr__(self):
        return f'[{self.character} in_word: {self.in_word} in_position: {self.in_position}]'
        

  


engine = create_engine('sqlite:///wordle.db')
Base.metadata.create_all(engine)