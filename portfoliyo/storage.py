from django.core.files.storage import get_storage_class
from storages.backends.s3boto import S3BotoStorage



class CachedS3BotoStorage(S3BotoStorage):
    """
    S3 storage backend that saves the files locally, too.

    Needed to integrate staticfiles, compressor, and S3.

    """
    def __init__(self, *args, **kwargs):
        super(CachedS3BotoStorage, self).__init__(*args, **kwargs)
        self.local_storage = get_storage_class(
            "compressor.storage.CompressorFileStorage")()

    def save(self, name, content):
        self.local_storage._save(name, content)
        content.file.seek(0)
        name = super(CachedS3BotoStorage, self).save(name, content)
        return name
