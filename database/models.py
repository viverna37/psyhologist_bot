from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Text, TIME, Boolean, Date
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# Создаем базовый класс для декларативных моделей
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True)
    username = Column(Text)
    name = Column(Text)
    birthday = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class Referral(Base):
    __tablename__ = 'referrals'

    id = Column(Integer, primary_key=True)
    referrer_id = Column(BigInteger)  # user_id из таблицы User
    referred_id = Column(BigInteger)  # user_id приглашённого
    timestamp = Column(DateTime, default=datetime.utcnow)


class UserDailyCard(Base):
    __tablename__ = 'user_daily_cards'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False, index=True)  # Telegram user_id
    last_card_date = Column(Date, nullable=False)  # Дата получения последней карты

class UserSupportCard(Base):
    __tablename__ = 'user_support_cards'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False, index=True, unique=True)  # Telegram user_id
    last_card_date = Column(Date, nullable=False)  # Дата получения последней карты
    free_uses_today = Column(Integer, default=0)  # Количество использований сегодня

class UserSubscription(Base):
    __tablename__ = 'user_subscriptions'
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True)
    type_subscription = Column(Integer)
    is_active = Column(Boolean)
    date_ended = Column(Date)

class UserBalance(Base):
    __tablename__ = 'user_balance'
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True)
    balance = Column(Integer, default=0)

class Utm(Base):
    __tablename__ = 'utms'
    id = Column(Integer, primary_key=True)
    statistics = Column(Integer, default=0)
    name = Column(Text)
