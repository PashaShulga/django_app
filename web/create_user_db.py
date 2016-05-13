from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from web.models import UserBD
import traceback
con = create_engine('postgresql+psycopg2://%s:%s@127.0.0.1:5432/postgres' % ('postgres', "Reload_777"))


def create_db(dbname, password, username):
    session = sessionmaker(bind=con)()
    session.connection().connection.set_isolation_level(0)
    try:
        session.execute("CREATE USER %s PASSWORD '%s'" % (username, password))
    except:
        print(traceback.format_exc())
    try:
        session.execute('CREATE DATABASE %s' % (dbname,))
    except:
        print(traceback.format_exc())
    try:
        session.execute('GRANT ALL PRIVILEGES ON DATABASE %s TO %s' % (dbname, username))
        session.connection().connection.set_isolation_level(1)
        add_user_in_maindb = UserBD(username=username, password=password, title=dbname)
        add_user_in_maindb.save()
    except:
        print(traceback.format_exc())
    finally:
        session.close()


    try:
        c = create_engine('postgresql+psycopg2://%s:%s@127.0.0.1:5432/%s' % (username, password, dbname))
        s = sessionmaker(bind=c)()
        s.connection().connection.set_isolation_level(0)
        s.execute("CREATE TABLE product(id SERIAL NOT NULL PRIMARY KEY)")
        # s.execute("CREATE TABLE files(id SERIAL NOT NULL PRIMARY KEY, file CHAR(255))")
        s.connection().connection.set_isolation_level(1)
    except:
        print(traceback.format_exc())

# session = sessionmaker(bind=con)()
# session.connection().connection.set_isolation_level(0)
