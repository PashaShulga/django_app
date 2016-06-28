from openpyxl import load_workbook
import os
from web.models import UserBD
from django.db import connections
from django.contrib import auth
import datetime
import csv


class XLSParse(object):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(BASE_DIR+'/static/files/')

    def __init__(self, file_name, request, table):
        self.file_name = str(file_name)
        self.request = request
        self.table = table

    def table_header(self, cursor, args):
        try:
            for it in args[0]:
                if it[1] == datetime.datetime:
                    it[1] = "DATE"
                elif it[1] == str:
                    it[1] = "VARCHAR(100)"
                elif it[1] == int:
                    it[1] = "INT"
                elif it[1] == float:
                    it[1] = "FLOAT"
                else:
                    it[1] = "VARCHAR(255)"
                cursor.execute("ALTER TABLE %s ADD %s %s" % (self.table, it[0].replace(" ", "_"), it[1]))
        except Exception as e:
            print(e)

    def queryset(self, *args, **kwargs):
        if auth.get_user(self.request):
            user_db = UserBD.objects.filter(username=auth.get_user(self.request).username)
            if user_db.exists():
                c = connections[auth.get_user(self.request).username].cursor()
                try:
                    title_list = []
                    c.execute("select column_name from information_schema.columns WHERE table_name = '%s'" % (self.table,))
                    res = c.fetchall()
                    if res != []:
                        self.table_header(c, args)
                        for it in res[1:]:
                            title_list.append(it[0])
                        for iter_ in args[1][1:]:
                            s = "insert into {} {}".format(self.table, tuple(title_list)).replace("'", '"')
                            s2 = ' VALUES {}'.format(tuple(iter_))
                            if None in iter_:
                                iter_[iter_.index(None)] = ''
                            c.execute(s+s2)
                    else:
                        c.execute('CREATE TABLE %s(id SERIAL NOT NULL PRIMARY KEY)' % (self.table,))
                        self.table_header(c, args)
                        title_list2 = []
                        c.execute("select column_name from information_schema.columns WHERE table_name = '%s'" % (self.table,))
                        res = c.fetchall()

                        for it in res[1:]:
                            title_list2.append(it[0])
                        for iter_ in args[1][1:]:
                            s = 'insert into {} {}'.format(self.table, tuple(title_list2)).replace("'", '"')
                            if None in iter_:
                                iter_[iter_.index(None)] = ''
                            s2 = ' VALUES {}'.format(tuple(iter_))
                            c.execute(s+s2)
                except Exception as e:
                    import traceback
                    print(traceback.format_exc())

    def xls_parse(self):
        wb = load_workbook(filename=self.path+self.file_name)
        sheet_ranges = wb[wb._sheets[0].title]

        counter = 0
        columns_name = []
        buff = []
        for item in sheet_ranges:
            buff.append(item)
            if counter >= 1:
                break
            counter += 1

        buff[0] = [k.value for k in buff[0]]
        buff[1] = [y.value for y in buff[1]]

        for y in buff[0]:
            for t in buff[1]:
                columns_name.append([y, type(t)])
                del buff[1][0]
                break

        k = 0
        d = []
        # while k < len(columns_name):
        for data in sheet_ranges:
            d.append([i.value.strftime('%Y-%m-%d %H:%M:%S') if type(i.value) == datetime.datetime else i.value for i in data])
            # k += 1
        self.queryset(columns_name, d)

    def csv_parse(self):
        # self.path+str(self._file)
        columns_name = []
        try:
            with open(self.path+str(self.file_name)) as csvfile:
                reader = csv.reader(csvfile)
                k = 0
                buff = []
                while k < 2:
                    for row in reader:
                        if row != []:
                            buff.append(row)
                            k += 1
                            break
                buff[0] = [k for k in buff[0]]
                buff[1] = [y for y in buff[1]]

                for y in buff[0]:
                    for t in buff[1]:
                        columns_name.append([y.replace("-", '').replace(" ", ''), type(t)])
                        del buff[1][0]
                        break
                k = 0
                data_ = []
                while k < len(columns_name):
                    for data in reader:
                        data_.append([i.strftime('%Y-%m-%d %H:%M:%S') if type(i) == datetime.datetime else i for i in data])
                    k += 1
            # print(columns_name, data_)
            self.queryset(columns_name, data_)
        except Exception as e:
            print(e)