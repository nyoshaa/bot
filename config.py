# переменные окружения
# python-dotenv нужен для настройки переменных окружения

import os
from dotenv import load_dotenv

load_dotenv()

# токен телеграмм бота
TOKEN: str = os.getenv("TOKEN")
# CLIENT_ID и CLIENT_SECRET - для доступа к апи Яндекс.Диска
# Получить - https://oauth.yandex.ru/client/new
CLIENT_ID: str = os.getenv("CLIENT_ID")
CLIENT_SECRET: str = os.getenv("CLIENT_SECRET")
CHECK_YADISK_INTERVAL: int = 30 * 60  # секунды (каждые 30 минут)
