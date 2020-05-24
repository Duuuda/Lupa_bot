from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine, Table, MetaData
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    coins = Column(Integer)

    def __init__(self, identifier, name, coins):
        self.id = identifier
        self.name = name
        self.coins = coins

    def __repr__(self):
        return f"<User('{self.id}','{self.name}', '{self.coins}')>"


def __create_session():
    engine = create_engine('sqlite:///user_data.db', echo=False)
    session = sessionmaker(bind=engine)
    return session()


def create_database():
    engine = create_engine('sqlite:///user_data.db', echo=False)
    metadata = MetaData()
    users_table = Table('users', metadata,
                        Column('id', Integer, primary_key=True),
                        Column('name', String),
                        Column('coins', Integer),
                        )
    metadata.create_all(engine)


def check_database(server_users):
    session = __create_session()
    database_users = session.query(User).all()
    session.close()
    # add_new_users_to_database
    if len(server_users) != len(database_users):
        database_id = [user.id for user in database_users]
        for user in server_users:
            if user.id not in database_id and not user.bot:
                add_user_to_database(user)
    # syncing_names
    for user in server_users:
        exist_user, session = get_user_from_database(user.id, get_session=True)
        if exist_user is not None and exist_user.name != user.display_name:
            exist_user.name = user.display_name
            session.commit()
            session.close()


def add_user_to_database(users):
    session = __create_session()
    if isinstance(users, (list, tuple)):
        for user in users:
            session.add(User(user.id, user.display_name, 0))
    else:
        session.add(User(users.id, users.display_name, 0))
    session.commit()
    session.close()


def get_user_from_database(search_parameter, get_session=False):
    session = __create_session()
    if isinstance(search_parameter, str):
        if get_session:
            return session.query(User).filter_by(name=search_parameter).first(), session
        session.close()
        return session.query(User).filter_by(name=search_parameter).first()
    if get_session:
        return session.query(User).filter_by(id=search_parameter).first(), session
    session.close()
    return session.query(User).filter_by(id=search_parameter).first()


def change_coins(user_param, change_amount):
    user, session = get_user_from_database(user_param, get_session=True)
    if user is not None:
        user.coins += change_amount
        session.commit()
        session.close()
    else:
        session.close()


def change_name(user_param, new_name):
    user, session = get_user_from_database(user_param, get_session=True)
    if user is not None:
        user.name = new_name
        session.commit()
        session.close()
    else:
        session.close()


def get_top_users(top_len):
    session = __create_session()
    all_users = session.query(User).all()
    session.close()
    all_users.sort(key=lambda user: user.coins, reverse=True)
    return all_users[:top_len]
