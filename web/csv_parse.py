import csv
import os
import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class CSVParse(object):
    def __init__(self, file_name, request):
        self._file = file_name
        self.request = request
        self.path = os.path.join(BASE_DIR + '/static/files/')

    def parse(self):
        # self.path+str(self._file)
        columns_name = []
        with open('../static/files/guest-list-626.csv') as csvfile:
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
            print(data_)
            print(columns_name)



CSVParse('s', 123).parse()
