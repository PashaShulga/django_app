import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class UploadHandler(object):
    def __init__(self, file, path=os.path.join(BASE_DIR+'/static/files/')):
        self._file = file
        self._path = path

    def handler(self):
        try:
            with open(self._path+str(self._file), 'wb+') as destination:
                for chunk in self._file.chunks():
                    destination.write(chunk)
                    print('Uploading...')
        except:
            pass
