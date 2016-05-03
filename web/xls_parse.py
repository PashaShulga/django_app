from openpyxl import load_workbook
import os
from web.models import UserBD
from django.db import connections
from django.contrib import auth
import datetime


class XLSParse(object):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(BASE_DIR+'/static/files/')

    def __init__(self, file_name, request):
        self.file_name = str(file_name)
        self.request = request

    def queryset(self, *args, **kwargs):
        if auth.get_user(self.request):
            user_db = UserBD.objects.filter(username=auth.get_user(self.request).username)
            if user_db.exists():
                c = connections[auth.get_user(self.request).username].cursor()
                try:
                    for it in args[0]:
                        if it[1] == datetime.datetime:
                            it[1] = "DATE"
                        elif it[1] == str:
                            it[1] = "CHARACTER(100)"
                        elif it[1] == int:
                            it[1] = "INT"
                        elif it[1] == float:
                            it[1] = "FLOAT"
                        else:
                            it[1] = "CHARACTER(255)"
                        c.execute("ALTER TABLE product ADD %s %s" % (it[0], it[1]))
                except:
                    pass
                try:
                    title_list = []
                    c.execute("select column_name from information_schema.columns WHERE table_name = 'product'")
                    for it in c.fetchall()[1:]:
                        title_list.append(it[0])
                    for iter_ in args[1][1:]:
                        s = 'insert into product {}'.format(tuple(title_list)).replace("'", '"')
                        s2 = ' VALUES {}'.format(tuple(iter_))
                        c.execute(s+s2)
                except Exception as e:
                    print(e)

    def parse(self):
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
        while k < len(columns_name):
            for data in sheet_ranges:
                d.append([i.value.strftime('%Y-%m-%d %H:%M:%S') if type(i.value) == datetime.datetime else i.value for i in data])
            k += 1
        self.queryset(columns_name, d)