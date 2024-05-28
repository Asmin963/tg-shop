class Pay:
    def __init__(self):
        self.merchant_id = ""
        pass

    def create_order(self, order_id: str | int, amount: float, desc: str, currency='RUB', lang='ru'):
        """

        Метод для генерации ссылки на заказ
        (Не реализован)

        """
        return

    def status_order(self):
        """

        Метод для проверки статуса платежа
        (Не реализован)

        """
        return True

    def delete_order(self):
        """

        Метод для удаления заказа
        (Не реализован)

        """
        return True

    def get_order(self):
        """

        Метод для получения заказа
        (Не реализован)

        """
        return True

    def get_orders(self):
        """

        Метод для получения списка заказов
        (Не реализован)

        """
        return True




