from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from web.models import UserBD
con = create_engine('postgresql+psycopg2://%s:%s@127.0.0.1:5432/postgres' % ('postgres', "Reload_777"))


def create_db(dbname, password, username='postgres'):
    try:
        session = sessionmaker(bind=con)()
        session.connection().connection.set_isolation_level(0)
        session.execute("CREATE USER %s PASSWORD '%s'" % (username, password))
        session.execute('CREATE DATABASE %s' % (dbname,))
        session.execute('GRANT ALL PRIVILEGES ON DATABASE %s TO %s' % (dbname, username))
        session.connection().connection.set_isolation_level(1)
    except Exception as e:
        print(e)


create_db('test_database_2', 'qwertyuiop', 'test_test')