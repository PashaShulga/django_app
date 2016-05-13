import csv
import os

class CSVParse(object):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(BASE_DIR+'/static/files/')

    def __init__(self, file_name, request):
        self.file_name = str(file_name)
        self.request = request

    def parse(self):
        pass