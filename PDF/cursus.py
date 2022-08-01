import math
from datetime import datetime
import os
from PyPDF2 import PdfFileReader, PdfFileWriter
import requests
import io

cur_year = str(datetime.now().year)[-2:]
semester = "eerste_semester"

vast = 0.5
buy_r = 0.0161
buy_rv = 0.0261
sell_r = 0.0186
sell_rv = buy_rv/buy_r * sell_r

buy_r_col = 0.0916
buy_rv_col = 0.17161
sell_r_col = sell_r/buy_r * buy_r_col
sell_rv_col = sell_r/buy_r * buy_rv_col


class Cursus:
    @staticmethod
    def get_years_back(nb_years):
        return str(int(cur_year) - nb_years)

    def __init__(self, is_same, barcode, pages_col, rv):
        self.is_same = is_same
        self.barcode = barcode
        self.pages_col = pages_col
        self.rv = rv
        self.f = None
        self.pdf = None
        self._pages_bw = -1

    def pages_bw(self):
        if self._pages_bw == -1:
            if self.is_same:
                self._pages_bw = self.previous_pdf().getNumPages() - self.pages_col
            else:
                # TODO
                pass
        return self._pages_bw

    def previous_pdf(self, years_back=1):
        if self.pdf is None:
            years = Cursus.get_years_back(years_back) + Cursus.get_years_back(years_back - 1)
            folder = "../Archief/" + years + "/"
            if os.path.isdir(folder):
                file = folder + semester + "/" + str(self.barcode) + ".pdf"
                if os.path.isfile(file):
                    self.f = open(file, "rb")
                    self.pdf = PdfFileReader(self.f)
                else:
                    return self.previous_pdf(years_back + 1)
            else:
                raise 'Could not find file in archive ' + str(self.barcode)
        return self.pdf

    def buy(self):
        if self.rv:
            return str(round(math.ceil((math.ceil(self.pages_bw()/2) * buy_rv + math.ceil(self.pages_col/2) * buy_rv_col + 0.5) * 1.06 * 100)/100, 2))
        else:
            return str(round(math.ceil((self.pages_bw() * buy_r + self.pages_col * buy_r_col + 0.5) * 1.06 * 100)/100, 2))

    def sell(self):
        if self.rv:
            return str(round(math.ceil((math.ceil(self.pages_bw()/2) * sell_rv + math.ceil(self.pages_col/2) * sell_rv_col + 0.5) * 1.02 * 1.06 * 10)/10, 2))
        else:
            return str(round(math.ceil((self.pages_bw() * sell_r + self.pages_col * sell_r_col + 0.5) * 1.02 * 1.06 * 10)/10, 2))

    def update(self):
        if self.is_same:
            r = requests.post('https://www.vtk.be/api/cudi/is-same', data=self.get_json())
            front_page = r.json()['front_page']
            url = 'https://www.vtk.be' + front_page
            print(url)
            response = requests.get(url)
            output = PdfFileWriter()
            p = io.BytesIO(response.content)
            front = PdfFileReader(p)

            if front.getNumPages() == 1:
                output.addPage(front.getPage(0))

            course = self.previous_pdf()
            for i in range(course.getNumPages()):
                if i != 0:
                    output.addPage(course.getPage(i))

            file = "../Archief/" + cur_year + self.get_years_back(-1) + "/" + semester + "/" + str(self.barcode) + ".pdf"
            with open(file, 'wb') as f:
                output.write(f)
        else:
            raise 'Not yet implemented'

    def get_json(self):
        if self.is_same:
            return {
                        "key": "99783417c1b06c8b39ae8025f5bfc937",
                        "is_same": str(self.is_same),
                        "barcode": "978" + Cursus.get_years_back(1) + cur_year + str(self.barcode),
                        "purchase_price": str(self.buy()),
                        "sell_price": str(self.sell())
                     }
        else:
            return{
                        "key": "99783417c1b06c8b39ae8025f5bfc937",
                        "is_same": str(self.is_same),
                        "barcode": "978" + Cursus.get_years_back(1) + cur_year + str(self.barcode),
                        "purchase_price": str(self.buy()),
                        "sell_price": str(self.sell()),
                        "black_white": str(self.pages_bw()),
                        "colored": str(self.pages_col),
                        "official": "True",
                        "recto_verso": str(self.rv)
                     }

    def __del__(self):
        if self.f is not None:
            self.f.close()
