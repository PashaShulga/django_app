# import os
# from web.models import UserDatafiles
#
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#
#
# class UploadHandler(object):
#     def __init__(self, file, user_id, path='/static/files/'):
#         self._file = file
#         self._path = os.path.join(BASE_DIR + path)
#         self.user_id = user_id
#         self.user_datafiles_id = 0
#
#     def handler(self):
#         with open(self._path + str(self._file), 'wb+') as destination:
#             try:
#                 for chunk in self._file.chunks():
#                     destination.write(chunk)
#                     print('Uploading...')
#                 self.user_datafiles_id = UserDatafiles(file_name=str(self._file), user_id=self.user_id)
#                 self.user_datafiles_id.save()
#                 self.user_datafiles_id = self.user_datafiles_id.id
#             except Exception as e:
#                 print(e)