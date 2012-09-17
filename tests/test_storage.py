"""Tests for custom compressor/staticfiles storage class."""
from compressor.storage import CompressorFileStorage
import mock

from portfoliyo import storage


def test_init(monkeypatch):
    """Init creates an instance of CompressorFileStorage, too."""
    monkeypatch.setattr(
        storage.S3BotoStorage, '__init__', lambda *a, **kw: None)

    s = storage.CachedS3BotoStorage()

    assert isinstance(s.local_storage, CompressorFileStorage)


def test_save(monkeypatch):
    """
    First saves to local storage, then seeks to 0, then saves to S3.

    This ordering is important, because otherwise if we are gzipping the
    version sent to S3, the S3 backend actually modifies content and we end up
    getting a gzipped version stored locally as well, which compressor can't
    handle.

    """
    monkeypatch.setattr(
        storage.S3BotoStorage, '__init__', lambda *a, **kw: None)
    def s3_save(self, name, content):
        content.file.seek('saved to s3')
        return name
    def c_save(self, name, content):
        content.file.seek('saved locally')
    monkeypatch.setattr(storage.S3BotoStorage, 'save', s3_save)
    monkeypatch.setattr(CompressorFileStorage, '_save', c_save)

    s = storage.CachedS3BotoStorage()

    mock_content = mock.Mock()
    s.save('name', mock_content)

    seek_args = [
        args[0] for args, kwargs in mock_content.file.seek.call_args_list]
    assert seek_args == ['saved locally', 0, 'saved to s3']
