import json
import os
from tools.logger import log


class Promocode:
    def __init__(self):
        self.file_path = os.path.join(os.path.dirname(__file__), "..", 'data')
        if not os.path.exists(self.file_path):
            os.makedirs(self.file_path)
        if not os.path.exists(os.path.join(self.file_path, 'promo.json')):
            with open(os.path.join(os.path.dirname(__file__), "..", 'data', 'promo.json'), 'w', encoding="utf-8") as f:
                json.dump({}, f)
        self.file_path = os.path.join(os.path.dirname(__file__), "..", 'data', 'promo.json')

    def get_promo_codes(self) -> dict:
        """
        Получение всех промокодов из файла.
        """
        try:
            with open(self.file_path, 'r', encoding="utf-8") as file:
                promo_codes = json.load(file)
            return promo_codes
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}

    def add_promo_code(self, promo_code: str, bonuses: int, max_uses: int) -> None | bool:
        """
        Добавление нового промокода с указанным количеством бонусов и максимальным количеством использований.
        """
        promo_codes = self.get_promo_codes()
        if promo_code not in promo_codes:
            promo_codes[promo_code] = {"bonuses": bonuses, "max_uses": max_uses, "uses": 0, "used_by": []}
            try:
                with open(self.file_path, 'w', encoding="utf-8") as file:
                    json.dump(promo_codes, file, indent=4)
                log(f'Записал новый промокод "{promo_code}" на {bonuses} бонусов с максимальным количеством использований {max_uses}')
                return True
            except Exception as e:
                log(f"Ошибка при записи нового промокода: {e}", lvl=4)
                return False
        else:
            log(f"Промокод '{promo_code}' уже добавлен.", lvl=4)
            return False

    def check_bonuses(self, promo_code: str):
        """
        Проверка количества бонусов для указанного промокода.
        """
        promo_codes = self.get_promo_codes()
        if promo_code in promo_codes:
            return promo_codes[promo_code]["bonuses"]
        else:
            return None

    def use_promo_code(self, promo_code: str, user_id: int) -> bool:
        """
        Использование промокода пользователем с указанным идентификатором.
        """
        promo_codes = self.get_promo_codes()
        if promo_code in promo_codes:
            if promo_codes[promo_code]["uses"] < promo_codes[promo_code]["max_uses"]:
                promo_codes[promo_code]["uses"] += 1
                promo_codes[promo_code]["used_by"].append(user_id)
                if promo_codes[promo_code]["uses"] >= promo_codes[promo_code]["max_uses"]:
                    log(f'Удалил промокод - {promo_codes[promo_code]}')
                    del promo_codes[promo_code]
                try:
                    with open(self.file_path, 'w', encoding="utf-8") as file:
                        json.dump(promo_codes, file, indent=4)
                except Exception as e:
                    log(f"Ошибка при использовании промокода: {e}", lvl=4)
                log(f'{user_id} использовал промокод "{promo_code}"')
                return True
            else:
                log(f"Промокод '{promo_code}' уже использован максимальное количество раз.", lvl=4)
                return False
        else:
            return False

    def check_promo_code_usage(self, promo_code: str, user_id: int) -> bool:
        """
        Проверка использовал ли указанный пользователь промокод.
        """
        promo_codes = self.get_promo_codes()
        if promo_code in promo_codes:
            return user_id in promo_codes[promo_code]["used_by"]
        else:
            return False

    def clear_all_promo_codes(self) -> bool:
        """
        Очистка всех промокодов.
        """
        try:
            with open(self.file_path, 'w', encoding="utf-8") as file:
                json.dump({}, file)
            log('Все промокоды были успешно очищены.')
            return True
        except Exception as e:
            log(f"Ошибка при очистке промокодов: {e}", lvl=4)
            return False

    def remove_promo_code(self, promo_code: str) -> bool:
        """
        Удаление одного промокода.
        """
        promo_codes = self.get_promo_codes()
        if promo_code in promo_codes:
            del promo_codes[promo_code]
            try:
                with open(self.file_path, 'w', encoding="utf-8") as file:
                    json.dump(promo_codes, file, indent=4)
                log(f'Промокод "{promo_code}" был успешно удален.')
                return True
            except Exception as e:
                log(f"Ошибка при удалении промокода '{promo_code}': {e}", lvl=4)
                return False
        else:
            log(f"Промокода '{promo_code}' не существует.", lvl=4)
            return False

    def update_promo_code_data(self, promo_code: str, bonuses: int, max_uses: int, uses: int) -> bool:
        """
        Изменение данных промокода.
        """
        promo_codes = self.get_promo_codes()
        if promo_code in promo_codes:
            promo_codes[promo_code]["bonuses"] = bonuses
            promo_codes[promo_code]["max_uses"] = max_uses
            promo_codes[promo_code]["uses"] = uses
            try:
                with open(self.file_path, 'w') as file:
                    json.dump(promo_codes, file, indent=4)
                log(f'Данные промокода "{promo_code}" успешно обновлены.')
                return True
            except Exception as e:
                log(f"Ошибка при обновлении данных промокода '{promo_code}': {e}", lvl=4)
                return False
        else:
            log(f"Промокода '{promo_code}' не существует.", lvl=4)
            return False

