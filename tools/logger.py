import logging
from time import strftime
import os
import inspect

from colorama import Fore, Style

from config import cfg

if not os.path.exists(cfg.LOG_PATH):
    os.makedirs(cfg.LOG_PATH)

logging.basicConfig(
    handlers=[logging.FileHandler(
        filename=f"{cfg.LOG_PATH}/{strftime('%Y-%m-%d_%H.%M.%S')}.log",
        encoding='utf-8', mode='a+')
    ],
    format="[%(asctime)s][%(filename)s] %(levelname)s: %(message)s",
    datefmt="%F %T",
    level=logging.INFO
)


def log(message: str, lvl: int = 1, prefix: str = 'Бот') -> None:
    """
    LVL:
    1 - info
    2 - error
    3 - warning
    4 - critical
    """
    line = inspect.stack()[1].lineno
    filename = inspect.stack()[1].filename.split("\\")[-1]
    if lvl == 1:
        logging.info(message)
        print(Fore.GREEN + f"[{strftime('%Y-%m-%d %H.%M.%S')}][{filename}][{line}] {prefix}: {message}" + Style.RESET_ALL)
    elif lvl == 2:
        logging.warning(message)
        print(Fore.BLUE + f"[{strftime('%Y-%m-%d %H.%M.%S')}][{filename}][{line}] {prefix}: {message}" + Style.RESET_ALL)
    elif lvl == 3:
        logging.error(message)
        print(Fore.YELLOW + f"[{strftime('%Y-%m-%d %H.%M.%S')}][{filename}][{line}] {prefix}: {message}" + Style.RESET_ALL)
    else:
        logging.critical(message)
        print(Fore.RED + f"[{strftime('%Y-%m-%d %H.%M.%S')}][{filename}][{line}] {prefix}: {message}" + Style.RESET_ALL)


def last_log_file():
    files = os.listdir(cfg.LOG_PATH)
    files.sort(key=lambda x: os.path.getmtime(os.path.join(cfg.LOG_PATH, x)), reverse=True)
    return files[0]


def cleare_last_log_files(count_files: int):
    files = os.listdir(cfg.LOG_PATH)
    files.sort(key=lambda x: os.path.getmtime(os.path.join(cfg.LOG_PATH, x)))
    for i in range(count_files):
        os.remove(os.path.join(cfg.LOG_PATH, files[i]))


def get_count_log_files():
    files = os.listdir(cfg.LOG_PATH)
    files.sort(key=lambda x: os.path.getmtime(os.path.join(cfg.LOG_PATH, x)), reverse=True)
    return len(files)


try:
    if get_count_log_files() > 10:
        cleare_last_log_files(get_count_log_files() - 10)
        log(f"Удалены лишние лог-файлы: {get_count_log_files() - 10}")
        log(f"Текущий лог-файл: {last_log_file()}")
except Exception as e:
    log(f"Ошибка при удалении лишних лог-файлов: {e}", lvl=2)
