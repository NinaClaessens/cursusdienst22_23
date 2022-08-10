import math
from datetime import datetime
import os
from PyPDF2 import PdfFileReader, PdfFileWriter
import requests
import io
import functools
import decimal

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

PDF_WIDTH, PDF_HEIGHT = 595.275, 841.889
PDF_REF_WIDTH, PDF_REF_HEIGHT = 210, 297
PDF_REF_MARGIN = 5
PDF_MARGIN_WIDTH = PDF_REF_MARGIN / PDF_REF_WIDTH * PDF_WIDTH
PDF_MARGIN_HEIGHT = PDF_REF_MARGIN / PDF_REF_HEIGHT * PDF_HEIGHT


def get_size(page):
    return page.mediaBox.getWidth(), page.mediaBox.getHeight()


def custom_sort(x, y):
    # return False if x is smaller
    a, b = str(x), str(y)
    minus = 1
    if len(b) < len(a):
        a, b = b, a
        minus = -1

    for i in range(len(x)):
        if a[i].isnumeric() and b[i].isnumeric():
            # check which number is smaller
            a_num = a[i]
            b_num = b[i]

            j = 1
            while i + j < len(a) and a[i + j].isnumeric():
                a_num += a[i + j]
                j += 1

            j = 1
            while i + j < len(b) and b[i + j].isnumeric():
                b_num += b[i + j]
                j += 1

            a_num, b_num = int(str(a_num)), int(str(b_num))
            if a_num != b_num:
                return (a_num - b_num) * minus

        elif a[i] != b[i]:
            return minus * 1 if a[i] > b[i] else -1 * minus
    return 0 if len(a) == len(b) else minus * -1


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
            print(f'{self.barcode} finished.')
        else:
            path = 'Veranderd/' + str(self.barcode) + '/'
            NO_PROBLEMS = True
            try:
                if os.path.isdir(path):
                    output = PdfFileWriter()
                    if self.rv:
                        output.addBlankPage(PDF_WIDTH, PDF_HEIGHT)

                    list_dir = sorted(os.listdir(path), key=functools.cmp_to_key(custom_sort))
                    for file in list_dir:
                        if NO_PROBLEMS:
                            full_path_file = path + file
                            print(full_path_file)
                            if file[-4:] == ".pdf":
                                slides = PdfFileReader(full_path_file, strict=False)
                                if slides.getNumPages() > 0:
                                    width_slides, height_slides = get_size(slides.getPage(0))

                                    if width_slides >= height_slides:  # slides, 2 per page
                                        ratio_width = decimal.Decimal(PDF_WIDTH - PDF_MARGIN_WIDTH * 2) / width_slides
                                        ratio_height = decimal.Decimal(PDF_HEIGHT - PDF_MARGIN_HEIGHT * 3) / (2 * height_slides)
                                        ratio = min(ratio_height, ratio_width)

                                        width_diff = (decimal.Decimal(PDF_WIDTH - PDF_MARGIN_WIDTH * 2) - width_slides * ratio) / 2
                                        height_diff = (decimal.Decimal(PDF_HEIGHT - PDF_MARGIN_HEIGHT * 3) - height_slides * ratio * 2) / 4

                                        for i in range(0, slides.getNumPages(), 2):
                                            new_page = output.addBlankPage(PDF_WIDTH, PDF_HEIGHT)

                                            new_page.mergeScaledTranslatedPage(slides.getPage(i), float(ratio),
                                                                               float(decimal.Decimal(PDF_MARGIN_WIDTH) + width_diff),
                                                                               float(ratio * height_slides + decimal.Decimal(PDF_MARGIN_HEIGHT * 2) + height_diff * 3))
                                            if i + 1 < slides.getNumPages():
                                                new_page.mergeScaledTranslatedPage(
                                                    slides.getPage(i + 1),
                                                    float(ratio),
                                                    float(decimal.Decimal(PDF_MARGIN_WIDTH) + width_diff),
                                                    float(decimal.Decimal(PDF_MARGIN_HEIGHT) + height_diff))

                                    else:  # course text
                                        if abs(decimal.Decimal(PDF_REF_WIDTH / PDF_REF_HEIGHT) - decimal.Decimal(width_slides / height_slides)) / decimal.Decimal(width_slides) >= 0.001:
                                            # ratios are weird
                                            NO_PROBLEMS = False
                                            print(f'{full_path_file} course text doesn\t match ratio of A4.')

                                        for i in range(slides.getNumPages()):
                                            output.addPage(slides.getPage(i))

                                    if self.rv and file != list_dir[-1] and output.getNumPages() % 2 == 0:
                                        output.addBlankPage()
                                else:
                                    # One of the files is corrupt
                                    print(f'{full_path_file} has no pages.')
                                    NO_PROBLEMS = False
                            else:
                                # One of the files is not a PDF
                                print(f'{full_path_file} is not a PDF.')
                                NO_PROBLEMS = False
                else:
                    NO_PROBLEMS = False
                    print(f'{self.barcode} does not yet have its new files.')

            except Exception as e:
                print('Catched exception', e)
                NO_PROBLEMS = False

            if NO_PROBLEMS:
                #  get front page
                self._pages_bw = output.getNumPages() + 1
                r = requests.post('https://www.vtk.be/api/cudi/is-same', data=self.get_json())
                front_page = r.json()['front_page']
                url = 'https://www.vtk.be' + front_page
                print(url)
                response = requests.get(url)
                p = io.BytesIO(response.content)
                front = PdfFileReader(p)
                output.insert_page(front.getPage(0))

                file = "../Archief/" + cur_year + self.get_years_back(-1) + "/" + semester + "/" + str(
                    self.barcode) + ".pdf"
                with open(file, 'wb') as f:
                    output.write(f)

                print(f'{self.barcode} finished.')



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
            return {
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