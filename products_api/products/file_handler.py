import hashlib
import pandas as pds

from django.core.files.uploadhandler import FileUploadHandler
from django.core.cache import cache
from django.core.files.uploadedfile import TemporaryUploadedFile

from .tasks import ingest_products_data_v2


class UploadProgressCachedHandler(FileUploadHandler):

    chunk_size = 64 * 2 ** 10  # 64KB chunk size

    def __init__(self, request=None):
        super(UploadProgressCachedHandler, self).__init__(request)
        self.upload_id = None
        self.cache_key = None
        self.h_sha256 = hashlib.sha256()

    def handle_raw_input(self, input_data, META, content_length, boundary, encoding=None):
        self.content_length = content_length
        self.upload_id = self.request.GET.get('upload_id', None)

        if self.upload_id:
            self.cache_key = f"{self.request.META['REMOTE_ADDR']}_{self.upload_id}"
            cache.set(self.cache_key, {
                'content_lenght': self.content_length,
                'uploaded': 0,
                'uploaded_percentage': 0,
            })

    def new_file(self, *args, **kwargs):
        super().new_file(*args, **kwargs)
        self.file = TemporaryUploadedFile(
            self.file_name, self.content_type, 0, self.charset, self.content_type_extra)

    def receive_data_chunk(self, raw_data, start):
        if self.cache_key:
            data = cache.get(self.cache_key)
            data['uploaded'] += self.chunk_size
            data['uploaded_percentage'] = (
                data['uploaded'] / data['content_lenght']) * 100
            data['uploaded_percentage'] = round(data['uploaded_percentage'], 2)
            cache.set(self.cache_key, data)

        self.file.write(raw_data)
        self.h_sha256.update(raw_data)
        return raw_data

    def file_complete(self, file_size):
        self.file.seek(0)
        self.file.size = file_size

        for chunk in pds.read_csv(self.file, chunksize=10000):
            ingest_products_data_v2.delay(chunk.to_dict("records"))

        self.file.close()

        return None

    def upload_complete(self):
        if self.cache_key:
            cache.delete(self.cache_key)
