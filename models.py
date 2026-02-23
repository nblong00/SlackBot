from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine("sqlite:///slackbot.db", echo = False)
Session = sessionmaker(bind = engine)
session = Session()
Base = declarative_base()


class Message(Base):
    __tablename__= "MessageCount"
    user_id = Column(String, primary_key=True)
    count = Column(Integer)

    def __repr__(self):
        return f"<Message_count(USER_ID: {self.user_id}, Count: {self.count})>"
    
Base.metadata.create_all(engine)
