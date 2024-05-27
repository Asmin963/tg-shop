import sqlite3
import os
import datetime as dt
from config import cfg
from tools.logger import log


class Database:
    def __init__(self):
        self.db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'base.db'))
        self.table_users = 'users'

        conn = sqlite3.connect(self.db_path)

        cursor = conn.cursor()

        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {self.table_users}
                          (user_id INTEGER PRIMARY KEY,
                           first_name TEXT,
                           last_name TEXT, 
                           lang_code TEXT,
                           username TEXT, 
                           register_date TEXT,
                           referals TEXT,
                           count_referals INTEGER,
                           from_referal TEXT,
                           buys INTEGER,
                           favorit_products TEXT,
                           balance INTEGER
                           )''')

        conn.close()

    def add_user(self, user_id, first_name, last_name, lang_code, username, from_referal=""):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(f'''INSERT INTO {self.table_users} (user_id, first_name, last_name, lang_code, username, register_date, 
            referals, count_referals, from_referal, buys, favorit_products, balance)
                               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
                           (
                           user_id, first_name, last_name, lang_code, username, dt.datetime.now(), "", 0, from_referal, 0, "", 0))

            conn.commit()
            log(f"Added user {user_id}", lvl=1)
        except sqlite3.IntegrityError as e:
            if "UNIQUE" in str(e):
                log(f"Пользователь {user_id} уже существует", lvl=2)
            else:
                log(f"Error adding user {user_id}: {str(e)}", lvl=3)
        except Exception as e:
            log(f"Error adding user {user_id}: {str(e)}", lvl=3)
        finally:
            conn.close()

    def update_user_column(self, user_id, column, value):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            if column in ['referals', 'favorit_products']:
                value = ','.join(value)

            cursor.execute(f'''UPDATE {self.table_users}
                               SET {column} = ?
                               WHERE user_id = ?''', (value, user_id))

            conn.commit()
            log(f"Updated user {user_id}'s {column} to {value}", lvl=1)
        except Exception as e:
            log(f"Error updating user {user_id}'s {column}: {str(e)}", lvl=3)
        finally:
            conn.close()

    def add_money_user(self, user_id, bonus):
        try:
            balance = int(self.get_user_column(user_id, 'balance'))
            if balance is None:
                balance = 0
            self.update_user_column(user_id, 'balance', balance + bonus)
            log(f"Added bonus {bonus} to user {user_id}", lvl=1)
            return True
        except Exception as e:
            log(f"Error adding bonus {bonus} to user {user_id}: {str(e)}", lvl=3)
            return False

    def refill_procent(self, user_id, bonus):
        """
        Начисляет пользователю, который пригласил user_id, проценты от пополнения
        Если user_id никем не приглашен, False
        :param user_id:
        :return:
        """
        try:
            from_referal = self.get_user_column(user_id, 'from_referal')
            if not from_referal:
                log(f'{user_id} никем не приглашён')
                return False
            partner = from_referal
            procent = cfg.GIFT_PROCENT_REFERAL / 100
            self.add_money_user(partner, bonus * procent)
            log(f'Начислено {procent * bonus} бонусов рефералу - {partner}, от пополнения пользователя {user_id}')
            return True
        except Exception as e:
            log(f'Ошибка при пополнении баланса пользователя {user_id}: {e}', lvl=4)
            return False

    def get_user_column(self, user_id, column='*'):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(f'''SELECT {column} FROM {self.table_users}
                               WHERE user_id = ?''', (user_id,))

            result = cursor.fetchone()
            if result:
                log(f"Retrieved user {user_id}'s {column}: {result}", lvl=1)
                if column == "*":
                    return UserInfo(result)
                if column in ['referals', 'favorit_products']:
                    result = result[0].split(',')
                else:
                    result = result[0]
                return result
            else:
                log(f"User {user_id} not found", lvl=1)
                return None
        except Exception as e:
            log(f"Error retrieving user {user_id}'s {column}: {str(e)}", lvl=3)
        finally:
            conn.close()

    def process_new_user(self, user_data):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(f'''INSERT INTO {self.table_users}
                               (user_id, first_name, last_name, lang_code, username, register_date, referals, count_referals, from_referal, buys, favorit_products, balance)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', user_data)

            conn.commit()
            log(f"Processed new user: {user_data}", lvl=1)
        except Exception as e:
            log(f"Error processing new user: {str(e)}", lvl=3)
        finally:
            conn.close()

    def get_user_registration_days(self, user_id):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(f'''SELECT register_date FROM {self.table_users}
                               WHERE user_id = ?''', (user_id,))

            result = cursor.fetchone()
            if result:
                register_date = dt.datetime.strptime(result[0], '%Y-%m-%d').date()
                days_since_registration = (dt.date.today() - register_date).days
                log(f"User {user_id} registered {days_since_registration} days ago", lvl=1)
                return days_since_registration
            else:
                log(f"User {user_id} not found for registration date", lvl=1)
                return None
        except Exception as e:
            log(f"Error retrieving user {user_id}'s registration date: {str(e)}", lvl=3)
        finally:
            conn.close()

    def get_users(self):
        """
        Возвращает список пользователей
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(f'''SELECT user_id FROM {self.table_users}''')
            result = [u[0] for u in cursor.fetchall()]
            log(f"Поучено {len(result)} пользователей", lvl=1)
        except Exception as e:
            log(f"Ошибка при получении юзеров: {str(e)}", lvl=3)
            result = None
        finally:
            conn.close()
            return result

    def get_columns(self, column):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(f'''SELECT {column} FROM {self.table_users}''')
            result = cursor.fetchall()
            log(f"Retrieved {len(result)} users", lvl=1)
        except Exception as e:
            log(f"Error retrieving users: {str(e)}", lvl=3)
            result = None
        finally:
            conn.close()
            return result

    def add_referal(self, user_id, referal_id):
        try:
            referals = self.get_user_column(user_id, "referals")
            referals = referals.split(",")
            if referal_id not in referals:
                referals.append(referal_id)
                self.update_user_column(user_id, "referals", referals)
                self.update_user_column(user_id, "count_referals", len(referals))
                return True
            return False
        except Exception as e:
            log(f"Error adding referal {referal_id} to user {user_id}: {str(e)}", lvl=3)
            return False


class UserInfo:
    def __init__(self, data):
        self.user_id = data[0]
        self.first_name = data[1]
        self.last_name = data[2]
        self.lang_code = data[3]
        self.username = data[4]
        self.register_date = data[5]
        self.referals = data[6]
        self.count_referals = data[7]
        self.from_referal = data[8]
        self.buys = data[9]
        self.favorit_products = data[10]
        self.balance = data[11]




