import logging
from sqlalchemy import Column, Integer, String, create_engine, delete, insert, select
from sqlalchemy.orm import declarative_base, Session
import telebot

from config import BOT_TOKEN

bot = telebot.TeleBot(BOT_TOKEN)

engine = create_engine("sqlite:///db/database.db")
Base = declarative_base()
logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO)

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)


class UserGroupAssociation(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    username = Column(String(255), nullable=True)
    group_name = Column(String(255), nullable=False)

# conn = sqlite3.connect('db/database.db', check_same_thread=False)
# cursor = conn.cursor()


def ping_group(ping_sender: str, ping_group: str, chat_id):
    with Session(engine) as session:
        stmt = select(UserGroupAssociation).where(
            UserGroupAssociation.chat_id == chat_id,
            UserGroupAssociation.group_name.ilike(ping_group),
        )
        result = session.execute(stmt)
        user_group_association = result.scalars().all()
        if user_group_association:
            user_tags = [f"@{x.username}" for x in user_group_association]
            bot.send_message(
                chat_id,
                f"{ping_sender} пингует группу {ping_group}\n{', '.join(user_tags)}",
            )
            return
    bot.send_message(chat_id, 'В такой группе нет людей')


@bot.message_handler(commands=['help', 'h'])
def start_message(message):
    bot.send_message(
        message.chat.id,
        'бот для тега групп людей\nкомманды:\n'
        '/add_group or /a, /remove_group or /r, /my_groups or /m,'
        ' /ping or /p, /remove_all_groups or /ra\n'
        'для того, что бы тегнуть калорантеров - /v or /valorant\n'
        'для доты - /d or /dota',
    )


@bot.message_handler(commands=['add_group', 'a'])
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


@bot.message_handler(commands=['remove_all_groups', 'ra'])
def remove_me_from_all_groups_message(message):
    with Session(engine) as session:
        stmt = delete(UserGroupAssociation).where(
            UserGroupAssociation.chat_id == message.chat.id,
            UserGroupAssociation.user_id == message.from_user.id,
        )
        session.execute(stmt)
        session.commit()

    bot.send_message(message.chat.id, 'Вы были удалены из всех групп')


@bot.message_handler(commands=['remove_group', 'r'])
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


@bot.message_handler(commands=['my_groups', 'm'])
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


@bot.message_handler(commands=['ping', 'p'])
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
    sender = message.from_user.username or "чел без ника"
    ping_group(chat_id=message.chat.id, ping_group=command, ping_sender=sender)


@bot.message_handler(commands=['valorant', 'v'])
def valorant_message(message):
    command = 'valorant'
    sender = message.from_user.username or "чел без ника"
    ping_group(chat_id=message.chat.id, ping_group=command, ping_sender=sender)


@bot.message_handler(commands=['dota', 'd'])
def dota_message(message):
    command = 'dota'
    sender = message.from_user.username or "чел без ника"
    ping_group(chat_id=message.chat.id, ping_group=command, ping_sender=sender)


@bot.message_handler(commands=['cs'])
def cs_message(message):
    command = 'cs'
    sender = message.from_user.username or "чел без ника"
    ping_group(chat_id=message.chat.id, ping_group=command, ping_sender=sender)


if __name__ == '__main__':
    bot.infinity_polling(skip_pending=True, logger_level=logging.INFO)
