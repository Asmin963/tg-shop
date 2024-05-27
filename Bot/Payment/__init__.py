from . import pay, orders_tg, orders_json
from .aaio_api import PaymentLinkGenerator
from config import cfg

JSON_Orders = orders_json.OrderManagerJSON(cfg.ORDERS_PATH)

merchant_id = cfg.MERCHANT_ID
secret = cfg.SECRET_KEY

aaio = PaymentLinkGenerator(merchant_id, secret)

OrdersBotHandler = orders_tg.OrdersBotMessageHandler()
refill = pay.Refill()



