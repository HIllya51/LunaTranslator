from ocrengines.baseocrclass import baseocr
import json, time, random, string
from requests import Requesters
from urllib.parse import parse_qs, urlparse

# https://github.com/dmMaze/BallonsTranslator/blob/dev/modules/ocr/ocr_google_lens.py


class OCR(baseocr):

    @staticmethod
    def _extract_ids_from_url(url_string: str):
        try:
            parsed_url = urlparse(url_string)
            query_params = parse_qs(parsed_url.query)
            vsrid = query_params.get("vsrid", [None])[0]
            lsessionid = query_params.get("lsessionid", [None])[0]
            return vsrid, lsessionid
        except Exception as e:
            # Логирование можно добавить сюда при необходимости, если self.logger доступен
            print(
                f"Error extracting IDs from URL {url_string}: {e}"
            )  # Просто вывод для примера
            return None, None

    def ocr(self, data):

        LENS_UPLOAD_ENDPOINT = "https://lens.google.com/v3/upload"
        LENS_METADATA_ENDPOINT = "https://lens.google.com/qfmetadata"
        # Обновленные заголовки из нового скрипта
        HEADERS = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "ru",  # Используем 'ru' как в новом скрипте, можно сделать параметром при желании
            "Cache-Control": "max-age=0",
            "Sec-Ch-Ua": '"Not-A.Brand";v="8", "Chromium";v="135", "Google Chrome";v="135"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
            "Origin": "https://www.google.com",  # Изменено
            "Referer": "https://www.google.com/",  # Изменено
            "Sec-Fetch-Site": "same-site",  # Изменено
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-User": "?1",
            "Priority": "u=0, i",  # Добавлено
        }

        random_filename = "".join(random.choices(string.ascii_letters, k=8))
        # Определяем расширение на основе mime-типа для имени файла

        mime = "image/png"
        ext = ".png"
        # Добавьте другие типы при необходимости

        filename = f"{random_filename}{ext}"

        files = {"encoded_image": (filename, data, mime)}
        # Параметры для запроса загрузки из нового скрипта
        params_upload = {
            "hl": "ru",  # Язык интерфейса Lens
            "re": "av",
            "vpw": "1903",  # Используем фиксированные значения из нового скрипта
            "vph": "953",  # Вместо dimensions, как в новом скрипте
            "ep": "gsbubb",
            "st": str(int(time.time() * 1000)),
        }

        # 1. Загрузка изображения
        upload_headers = HEADERS.copy()
        response_upload = self.proxysession.post(
            LENS_UPLOAD_ENDPOINT,
            headers=upload_headers,
            files=files,
            params=params_upload,
            requester=Requesters.winhttp,
        )
        response_upload.raise_for_status()  # Проверка на HTTP ошибки

        final_url = str(response_upload.url)  # URL после редиректов
        # 2. Извлечение ID сессии
        vsrid, lsessionid = self._extract_ids_from_url(final_url)
        if not vsrid or not lsessionid:
            raise Exception(
                "Failed to extract vsrid or lsessionid from upload redirect URL."
            )

        # 3. Запрос метаданных
        metadata_params = {
            "vsrid": vsrid,
            "lsessionid": lsessionid,
            "hl": params_upload["hl"],
            "qf": "CAI%3D",
            "st": str(int(time.time() * 1000)),
            "vpw": params_upload["vpw"],
            "vph": params_upload["vph"],
            "source": "lens",
        }
        # Модифицированные заголовки для запроса метаданных из нового скрипта
        metadata_headers = HEADERS.copy()
        metadata_headers.update(
            {
                "Accept": "*/*",
                "Referer": final_url,  # Важно указать реферер
                "Sec-Fetch-Site": "same-origin",  # Изменено
                "Sec-Fetch-Mode": "cors",  # Изменено
                "Sec-Fetch-Dest": "empty",  # Изменено
                "Priority": "u=1, i",  # Изменено
            }
        )
        # Удаляем ненужные для этого запроса заголовки
        metadata_headers.pop("Upgrade-Insecure-Requests", None)
        metadata_headers.pop("Sec-Fetch-User", None)
        metadata_headers.pop("Cache-Control", None)
        metadata_headers.pop("Origin", None)  # Origin не нужен для GET

        response_metadata = self.proxysession.get(
            LENS_METADATA_ENDPOINT,
            headers=metadata_headers,
            params=metadata_params,
            requester=Requesters.winhttp,
        )
        response_metadata.raise_for_status()

        try:
            response_text = response_metadata.text
            # Убираем префикс, если он есть
            if response_text.startswith(")]}'\n"):
                response_text = response_text[5:]
            elif response_text.startswith(")]}'"):
                response_text = response_text[4:]

            # Используем json5 для парсинга
            metadata_json = json.loads(response_text)
            res = []
            for __ in metadata_json[0][2][0][0]:
                res.append("".join(_[1] for _ in __[1][0][0]))
            return res
        except:
            raise Exception(response_metadata)
