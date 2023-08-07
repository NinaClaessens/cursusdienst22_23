import math

vast = 0.5
buy_r = 0.0165
buy_rv = 0.0267
sell_r = buy_r*1.03
sell_rv = buy_rv/buy_r * sell_r

Continue = True

while Continue:
    pages = int(input('nb of pages'))
    rv = input('rv?')
    if rv == '1' or rv == 'True' or rv == "rv":
        print(round(math.ceil((math.ceil(pages/2) * buy_rv + vast) * 1.06 * 100)/100, 2))
        print(round(math.ceil((math.ceil(pages/2) * sell_rv + vast) * 1.06 * 1.02 * 10)/10, 2))
    else:
        print(round(math.ceil((pages * buy_r + vast) * 1.06 * 100) / 100, 2))
        print(round(math.ceil((pages * sell_r + vast) * 1.06 * 1.02 * 10) / 10, 2))
