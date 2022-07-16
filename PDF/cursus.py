class Cursus:
    def __init__(self, is_same, barcode, pages_bw, pages_col, rv, buy, sell):
        self.is_same = is_same
        self.barcode = barcode
        self.pages_bw = pages_bw
        self.pages_col = pages_col
        self.rv = rv
        self.buy = buy
        self.sell = sell

    def get_json(self):
        if self.is_same:
            return '{"key": "99783417c1b06c8b39ae8025f5bfc937", ' \
                   '"is_same": "' + str(self.is_same).lower() + '", ' \
                   '"barcode": "' + str(self.barcode) + '"}'
        else:
            return '{"key": "99783417c1b06c8b39ae8025f5bfc937", ' \
                 '"is_same": "' + str(self.is_same).lower() + '", ' \
                 '"barcode": "' + str(self.barcode) + '", ' \
                 '"black_white": "' + str(self.pages_bw) + '", ' \
                 '"colored": "' + str(self.pages_col) + '", ' \
                 '"official": "true", ' \
                 '"recto_verso": "' + str(self.rv).lower() + '", ' \
                 '"buy_price": "' + str(self.buy) + '", ' \
                 '"sell_price": "' + str(self.sell) + '" }'
