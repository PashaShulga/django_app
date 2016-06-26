from weasyprint import HTML, CSS


class PDFMaker(object):
    def __init__(self, host, html, file_name):
        self.host = host
        self.html = html
        self.file_name = file_name

    def make(self):
        logo = """<img src="http://{}/static/images/logo_datavisie.png" style="width: 200px"> """.format(self.host)
        if self.html is not None:
            HTML(string=logo + self.html).write_pdf('static/reports/%s.pdf' % (self.file_name))
        else:
            raise Exception('HTML is not correct')
