__all__ = [
  "yadisk"
]

import datetime as dt
import yadisk

from config import CLIENT_ID, CLIENT_SECRET

# Документация по API Яндекс.Диска - https://yadisk.readthedocs.io/ru/latest/intro.html
class YandexDisk():
  """Класс для удобной работы с API Яндекс.Диска.

  Атрибуты:
      token (str | None): Токен доступа к API Яндекс.Диска. По умолчанию None.

  Методы:
      check_for_recent_updates(path, last_check): Проверяет наличие обновлений в папке Яндекс.Диска. Возвращает bool
      get_code_url(): Возвращает URL для получения кода авторизации.
      get_token_from_code(code): Получает и сохраняет токен доступа, используя код авторизации.
  """

  def __init__(self, token: str | None = None):
      """
      Инициализирует объект класса YandexDisk.

      Параметры:
          token (str | None): Токен доступа к API Яндекс.Диска. По умолчанию None.
      """

      self.token = token

  def check_for_recent_updates(self, path, last_check) -> bool:
      """
      Проверяет наличие обновлений в папке Яндекс.Диска.

      Параметры:
          path (str): Путь к папке на Яндекс.Диске.
          last_check (dt.datetime): Дата последней проверки.

      Возвращает:
          bool: True, если в папке есть обновления, иначе False.
      """
      with yadisk.Client(token=self.token) as client:
          for item in client.listdir(path):
              if item.created > last_check or item.modified > last_check:
                  return True
      return False

  def get_code_url(self) -> str:
      """
      Возвращает URL для получения кода авторизации.

      Возвращает:
          str: URL для получения кода авторизации.
      """
      with yadisk.Client(CLIENT_ID, CLIENT_SECRET) as client:
          url = client.get_code_url()
          return url

  def get_token_from_code(self, code: str) -> str | None:
      """
      Получает и сохраняет токен доступа, используя код авторизации.

      Параметры:
          code (str): Код авторизации.

      Возвращает:
          str | None: Токен доступа, если авторизация прошла успешно. В противном случае None.
      """
      with yadisk.Client(CLIENT_ID, CLIENT_SECRET) as client:
          response = client.get_token(code)
          client.token = response.access_token
          if not client.check_token:
              # при обработке токена произошла ошибка, токен неверен
              return None
          # с токеном все ок
          self.token = client.token
          return client.token
