import os
import shutil
import time
from os import path

from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

Base = declarative_base()


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True)  # user_id
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    status = Column(String)
    user_hash = Column(Integer)
    attempt = Column(Integer)
    invite_link = Column(String)
    username = Column(String)

    def __repr__(self):
        return f"<Profile(" \
               f"id={self.id}, " \
               f"first_name={self.first_name}, " \
               f"last_name={self.last_name}, " \
               f"email={self.email}, " \
               f"status={self.status}, " \
               f"user_hash={self.user_hash}, " \
               f"attempt={self.attempt}, " \
               f"invite_link={self.invite_link}, " \
               f"username={self.username})>"

    def to_dict(self):
        return {column.name: getattr(self, self.__mapper__.get_property_by_column(column).key)
                for column in self.__table__.columns}


class DB:

    def __init__(self, filename, only_read=False, debug=False):

        if path.isfile(filename) and not only_read:
            data_dir = path.dirname(filename)
            fname = path.basename(filename)

            backup_dir = path.join(data_dir, "backups")
            if not path.isdir(backup_dir):
                os.mkdir(backup_dir)
            backup_file = path.join(backup_dir, f"{fname}_{int(time.time())}")

            print("Copying {} to {}".format(filename, backup_file))

            shutil.copy(filename, backup_file)

        self.engine = create_engine(
            f'sqlite:///{filename}',
            connect_args={'check_same_thread': False},
            echo=debug
        )


        Session = scoped_session(sessionmaker(bind=self.engine))
        self.session = Session()

        Base.metadata.create_all(self.engine)

    def add_record(self, obj, do_flush=True):
        """
        Add record to Database.
        :Profile obj: Profile to record in Database.
        :bool do_flush: If need to commit Database.
        :return: None
        """
        self.session.add(obj)
        if do_flush:
            self.flush()

    def update_record(self, obj, do_flush=True):

        query_profile = self.session.query(Profile).filter(Profile.id == obj["id"])
        if query_profile.count() == 0:
            self.add_record(obj=obj, do_flush=do_flush)
        elif query_profile.count() == 1:
            query_profile.update(obj.to_dict())
            if do_flush:
                self.flush()
        else:
            raise Exception('Wrong base structure!')

    def flush(self):
        self.session.commit()
        self.session.flush()


class ProfileDB(DB):

    def __init__(self, file):
        # self.db =
        self.session = DB(file).session

    def add_profile(self, dict_profile):
        self.add_record(Profile(**dict_profile))

    def update_profile(self, dict_profile):
        query = self.session.query(Profile)
        query_profile = query.filter(Profile.id == dict_profile["id"])
        if query_profile.count() == 0:
            self.add_profile(dict_profile)
        elif query_profile.count() == 1:
            query_profile.update(dict_profile)
        else:
            raise Exception('Wrong base structure!')

    def get_all(self):
        return self.session.query(Profile).all()

    @property
    def all_ids_approved(self):
        return {profile.id for profile in self.get_by_status(status="approved")}

    def get_by_id(self, q_id):
        query = self.session.query(Profile)
        profiles = query.filter(Profile.id == q_id).all()
        assert len(profiles) <= 1, 'problem'

        profile = profiles[0] if len(profiles)==1 else None
        return profile

    def get_by_invite_link(self, invite_link):
        query = self.session.query(Profile)
        users = query.filter(Profile.invite_link == invite_link).all()
        return users

    def get_by_status(self, status):
        query = self.session.query(Profile)
        users = query.filter(Profile.status == status).all()
        return users

    def get_by_username(self, username):
        query = self.session.query(Profile)
        users = query.filter(Profile.username == username).all()
        assert len(users) == 1
        return users[0]


if __name__ == "__main__":
    pass
    # db_main = DB("main.sqlite")
    # profile_db = ProfileDB(db_main)
    # profile_db = ProfileDB("main.sqlite")
    #
    # tmp_dict_profile = {key: None for key in USER_DATA_KEYS}
    # tmp_dict_profile['id'] = 1
    # tmp_dict_profile['username'] = "third"
    # tmp_dict_profile['status'] = "approved"
    # profile_db.update_profile(tmp_dict_profile)
    # print('first', profile_db.all_ids_approved)
