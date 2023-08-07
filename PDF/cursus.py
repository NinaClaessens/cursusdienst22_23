import math
from datetime import datetime
import os
from PyPDF2 import PdfReader, PdfWriter, Transformation, PageObject
import requests
import io
import functools
import decimal
import traceback
from PyPDF2._utils import CompressedTransformationMatrix

cur_year = "23"
semester = "eerste_semester"

vast = 0.5
buy_r = 0.0165
buy_rv = 0.0267
sell_r = buy_r*1.03
sell_rv = buy_rv/buy_r * sell_r

buy_r_col = 0.0939
buy_rv_col = 0.1878
sell_r_col = sell_r/buy_r * buy_r_col
sell_rv_col = sell_r/buy_r * buy_rv_col

PDF_WIDTH, PDF_HEIGHT = 595, 842
PDF_REF_WIDTH, PDF_REF_HEIGHT = 210, 297
PDF_REF_MARGIN = 5
PDF_MARGIN_WIDTH = PDF_REF_MARGIN / PDF_REF_WIDTH * PDF_WIDTH
PDF_MARGIN_HEIGHT = PDF_REF_MARGIN / PDF_REF_HEIGHT * PDF_HEIGHT


def get_size(page):
    return page.mediabox.width, page.mediabox.height


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
                self._pages_bw = len(self.previous_pdf().pages) - self.pages_col
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
                    self.pdf = PdfReader(self.f)
                else:
                    return self.previous_pdf(years_back + 1)
            else:
                raise Exception('Could not find file in archive ' + str(self.barcode))
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
            output = PdfWriter()
            p = io.BytesIO(response.content)
            front = PdfReader(p)

            if len(front.pages) == 1:
                output.add_page(front.pages[0])

            course = self.previous_pdf()
            for i in range(len(course.pages)):
                if i != 0:
                    output.add_page(course.pages[i])

            file = "../Archief/" + cur_year + self.get_years_back(-1) + "/" + semester + "/" + str(self.barcode) + ".pdf"
            with open(file, 'wb') as f:
                output.write(f)
            print(f'{self.barcode} finished.')
        else:
            path = 'Veranderd/' + str(self.barcode) + '/'
            NO_PROBLEMS = True
            try:
                if os.path.isdir(path):
                    output = PdfWriter()
                    if self.rv:
                        output.add_blank_page(PDF_WIDTH, PDF_HEIGHT)

                    list_dir = sorted(os.listdir(path), key=functools.cmp_to_key(custom_sort))
                    for file in list_dir:
                        if NO_PROBLEMS:
                            full_path_file = path + file
                            print(full_path_file)
                            if file[-4:] == ".pdf":
                                slides = PdfReader(full_path_file, strict=False)
                                if len(slides.pages) > 0:
                                    width_slides, height_slides = get_size(slides.pages[0])

                                    if decimal.Decimal(1.2) * width_slides >= height_slides:  # slides, 2 per page
                                        ratio_width = decimal.Decimal(PDF_WIDTH - PDF_MARGIN_WIDTH * 2) / width_slides
                                        ratio_height = decimal.Decimal(PDF_HEIGHT - PDF_MARGIN_HEIGHT * 3) / (2 * height_slides)
                                        ratio = min(ratio_height, ratio_width)

                                        width_diff = (decimal.Decimal(PDF_WIDTH - PDF_MARGIN_WIDTH * 2) - width_slides * ratio) / 2
                                        height_diff = (decimal.Decimal(PDF_HEIGHT - PDF_MARGIN_HEIGHT * 3) - height_slides * ratio * 2) / 4

                                        for i in range(0, len(slides.pages), 2):
                                            new_page = PageObject().create_blank_page(width=PDF_WIDTH, height=PDF_HEIGHT)

                                            if i + 1 < len(slides.pages):
                                                slides.pages[i+1].mediabox.right = PDF_WIDTH
                                                slides.pages[i+1].mediabox.top = PDF_HEIGHT
                                                # calculate parameters
                                                op = (
                                                    Transformation()
                                                    .scale(float(ratio))
                                                    .translate(
                                                        int(decimal.Decimal(PDF_MARGIN_WIDTH) + width_diff),
                                                        int(decimal.Decimal(PDF_MARGIN_HEIGHT) + height_diff)
                                                    )
                                                )
                                                slides.pages[i+1].add_transformation(op)
                                                new_page.merge_page(slides.pages[i+1])

                                            op = (
                                                Transformation()
                                                .scale(float(ratio))
                                                .translate(
                                                    int(decimal.Decimal(PDF_MARGIN_WIDTH) + width_diff),
                                                    int(decimal.Decimal(ratio) * height_slides + decimal.Decimal(
                                                        PDF_MARGIN_HEIGHT * 2) + height_diff * 3)
                                                )
                                            )

                                            slides.pages[i].mediabox.right = PDF_WIDTH
                                            slides.pages[i].mediabox.top = PDF_HEIGHT
                                            slides.pages[i].add_transformation(op)
                                            new_page.merge_page(slides.pages[i])

                                            output.add_page(new_page)


                                    else:  # course text
                                        if abs(decimal.Decimal(PDF_REF_WIDTH / PDF_REF_HEIGHT) - decimal.Decimal(width_slides / height_slides)) / decimal.Decimal(width_slides) >= 0.001:
                                            # ratios are weird
                                            NO_PROBLEMS = False
                                            print(f'{full_path_file} course text doesn\t match ratio of A4.')

                                        for i in range(len(slides.pages)):
                                            output.add_page(slides.pages[i])

                                    if self.rv and file != list_dir[-1] and len(output.pages) % 2 == 0:
                                        output.add_blank_page(PDF_WIDTH, PDF_HEIGHT)
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
                self._pages_bw = len(output.pages) + 1 - self.pages_col
                r = requests.post('https://www.vtk.be/api/cudi/is-same', data=self.get_json())
                front_page = r.json()['front_page']
                url = 'https://www.vtk.be' + front_page
                print(url)
                response = requests.get(url)
                p = io.BytesIO(response.content)
                front = PdfReader(p)
                output.insert_page(front.pages[0])

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