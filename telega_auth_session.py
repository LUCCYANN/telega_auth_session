import os
import json
import random
from pathlib import Path
from telethon import TelegramClient
import re
import logging
import asyncio
from telethon.errors import PhoneNumberBannedError
import sys
import locale

# Установка кодировки консоли на UTF-8 для корректного вывода логов на любом языке
sys.stdout.reconfigure(encoding='utf-8')
locale.setlocale(locale.LC_ALL, '')

def get_proxy():
    proxy = {
        'proxy_type': 'http',
        'addr': '[[PROXY_IP]]',
        'port': '[[PROXY_PORT]]',
        'username': '[[PROXY_LOGIN]]',
        'password': '[[PROXY_PASS]]',
        'rdns': True
    }
    return proxy


def get_client(session_path):
    session_path = Path(session_path)
    session_name = os.path.basename(session_path).replace('.session', '')
    path = str(session_path).replace(f'{session_name}.session', '')

    name = str(Path(path) / session_name)
        
    session_path = f'{name}.session'
    json_path = f'{name}.json'
    
    session_json_backup = {
        "app_id": 2040,
        "app_hash": 'b18441a1ff607e10a989891a5462e627',
        "device": 'PC 64bit',
        "sdk": '4.16.30-vxCUSTOM',
        "app_version": '3.1.8 x64',
        "lang_pack": 'en',
        "system_lang_pack": 'en-US'
    }
    
    session_json_exist = {}
    if os.path.exists(json_path):
        with open(json_path) as f_in:
            session_json_exist = json.load(f_in)

    values_list = ['app_id', 'app_hash', 'device', 'sdk', 'app_version', 'lang_pack', 'system_lang_pack']
    session_json = session_json_exist
    for value in values_list:
        if value in session_json_exist:
            pass
        else:
            session_json = session_json_backup
            break
    proxy = get_proxy()
    client = TelegramClient(
        session=session_path,
        api_id=session_json['app_id'],
        api_hash=session_json['app_hash'],
        proxy=proxy,
        device_model=session_json['device'],
        system_version=session_json['sdk'],
        app_version=session_json['app_version'],
        lang_code=session_json['lang_pack'],
        system_lang_code=session_json['system_lang_pack']
    )
    
    return client

def load_phone_number(session_path):
    # Функция для загрузки номера телефона из JSON-файла
    json_path = session_path.replace('.session', '.json')
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('phone', None)  # Получение номера телефона
    return None

async def main():
    client = get_client('[[ACC_SESSION_FILE_PATH]]')
    phone_number = load_phone_number('[[ACC_SESSION_FILE_PATH]]')

    if phone_number is None:
        raise ValueError("Phone number have not been found in JSON-file.")

    # Настройка логгера
    logging.getLogger('telethon').setLevel(logging.WARNING)

    logger = logging.getLogger('__main__')
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    try:
        await client.connect()
        if await client.is_user_authorized():
            logger.info("SESSION IS VALID")
        else:
            logger.info("SESSION IS INVALID")
    except PhoneNumberBannedError:
        logger.error(f"Phone Number {phone_number} Has been blocked by Telegram.")
    except Exception as e:
        logger.error(f"Error commited: {e}")
    finally:
        await client.disconnect()

# Запуск асинхронной функции main
asyncio.run(main())
