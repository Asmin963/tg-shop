import hashlib
from urllib.parse import urlencode
from tools.logger import log


class PaymentLinkGenerator:
    def __init__(self, merchant_id, secret):
        self.merchant_id = merchant_id
        self.secret = secret

    def generate_payment_link(self, order_id, amount, currency='RUB', desc='Order Payment', lang='ru'):
        try:
            sign = f':'.join([
                str(self.merchant_id),
                str(amount),
                str(currency),
                str(self.secret),
                str(order_id)
            ])

            params = {
                'merchant_id': self.merchant_id,
                'amount': amount,
                'currency': currency,
                'order_id': order_id,
                'sign': hashlib.sha256(sign.encode('utf-8')).hexdigest(),
                'desc': desc,
                'lang': lang
            }

            payment_link = "https://aaio.so/merchant/pay?" + urlencode(params)
            return payment_link
        except Exception as e:
            log(f'Ошибка при генерации ссылки на оплату: {e}', lvl=4)
            return "https://aaio.so/"

