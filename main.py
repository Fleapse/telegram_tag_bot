from sqlalchemy import Column, Integer, String, create_engine, delete, insert, select
from sqlalchemy.orm import declarative_base, Session
import telebot

from config import BOT_TOKEN

bot = telebot.TeleBot(BOT_TOKEN)

engine = create_engine("sqlite:///db/database.db")
Base = declarative_base()


class UserGroupAssociation(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    username = Column(String(255), nullable=True)
    group_name = Column(String(255), nullable=False)

# conn = sqlite3.connect('db/database.db', check_same_thread=False)
# cursor = conn.cursor()


@bot.message_handler(commands=['help'])
def start_message(message):
    bot.send_message(message.chat.id, 'бот для тега групп людей\nкомманды:\n/add_group, /remove_group, /my_groups, /ping')


@bot.message_handler(commands=['add_group'])
def add_me_to_group_message(message):
    commands = message.text.strip().split(maxsplit=1)
    if len(commands) == 1:
        bot.send_message(
            message.chat.id,
            'Вы не указали название группы в которую вас нужно добавить'
        )
        return
    command = commands[1]
    if ' ' in command:
        bot.send_message(message.chat.id, 'группа должна быть одним словом')
        return
    with Session(engine) as session:
        stmt = select(UserGroupAssociation).where(
            UserGroupAssociation.chat_id == message.chat.id,
            UserGroupAssociation.user_id == message.from_user.id,
            UserGroupAssociation.group_name == command
        )
        result = session.execute(stmt)
        user_group_association = result.scalars().one_or_none()
        if user_group_association:
            bot.send_message(
                message.chat.id,
                'Вы уже в этой группе'
            )
            return
        stmt = insert(UserGroupAssociation).values(
            chat_id=message.chat.id,
            user_id=message.from_user.id,
            username=message.from_user.username,
            group_name=command,
        )
        session.execute(stmt)
        session.commit()

    bot.send_message(message.chat.id, f'Вы были добавленны в группу {command}')


@bot.message_handler(commands=['remove_group'])
def remove_me_from_group_message(message):
    commands = message.text.strip().split(maxsplit=1)
    if len(commands) == 1:
        bot.send_message(
            message.chat.id,
            'Вы не указали название группы из которой вас исключить'
        )
        return
    command = commands[1]
    if ' ' in command:
        bot.send_message(message.chat.id, 'группа должна быть одним словом')
        return
    with Session(engine) as session:
        stmt = select(UserGroupAssociation).where(
            UserGroupAssociation.chat_id == message.chat.id,
            UserGroupAssociation.user_id == message.from_user.id,
            UserGroupAssociation.group_name == command
        )
        result = session.execute(stmt)
        user_group_association = result.scalars().one_or_none()
        if not user_group_association:
            bot.send_message(
                message.chat.id,
                'вас нет в этой группе'
            )
            return
        stmt = delete(UserGroupAssociation).where(
            UserGroupAssociation.chat_id == message.chat.id,
            UserGroupAssociation.user_id == message.from_user.id,
            UserGroupAssociation.group_name == command
        )
        session.execute(stmt)
        session.commit()

    bot.send_message(message.chat.id, f'Вы были удалены из группы {command}')


@bot.message_handler(commands=['my_groups'])
def show_my_groups_message(message):
    with Session(engine) as session:
        stmt = select(UserGroupAssociation).where(
            UserGroupAssociation.chat_id == message.chat.id,
            UserGroupAssociation.user_id == message.from_user.id,
        )
        result = session.execute(stmt)
        user_group_association = result.scalars().all()
        if user_group_association:
            groups = ', '.join([x.group_name for x in user_group_association])
            bot.send_message(
                message.chat.id,
                f'Вы состоите в {len(user_group_association)} группах:\n {groups}'
            )
            return
    bot.send_message(message.chat.id, 'Вы не состоите ни в одной группе')


@bot.message_handler(commands=['ping'])
def ping_message(message):
    commands = message.text.strip().split(maxsplit=1)
    if len(commands) == 1:
        bot.send_message(
            message.chat.id,
            'Вы не указали название группы, которую нужно пингануть'
        )
        return
    command = commands[1]
    if ' ' in command:
        bot.send_message(message.chat.id, 'группа должна быть одним словом')
        return
    with Session(engine) as session:
        stmt = select(UserGroupAssociation).where(
            UserGroupAssociation.chat_id == message.chat.id,
            UserGroupAssociation.group_name == command
        )
        result = session.execute(stmt)
        user_group_association = result.scalars().all()
        if user_group_association:
            user_tags = [f"@{x.username}" for x in user_group_association]
            bot.send_message(
                message.chat.id,
                ', '.join(user_tags),
            )
            return
    bot.send_message(message.chat.id, 'В такой группе нет людей')


if __name__ == '__main__':
    bot.polling(none_stop=True)
