import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from requests_toolbelt import MultipartEncoder

from loguru_conf import logger

session = requests.Session()
session.trust_env = False


class CustomFileStorage(Storage):
    def _save(self, name, content):
        data = {
            "file": (name, content, "multipart-form-data"),
        }
        form_data = MultipartEncoder(data)
        response = session.post(
            settings.MEGADRIVE_SERVER_URL,
            data=form_data,
            headers={"Content-Type": form_data.content_type},
        )
        logger.debug(
            f"UPLOAD FILE MEGADRIVE: {response.status_code} {response.json()}"
        )
        data = response.json() if response.status_code == 200 else None
        file_url = data.get("downloadUri")
        name = (
            settings.MEGADRIVE_MIR
            + file_url[file_url.index("/file") :]  # noqa
        )
        return name

    def _open(self, name, mode="rb"):
        return ContentFile(name)

    def url(self, name):
        return name

    def exists(self, name):
        return False
