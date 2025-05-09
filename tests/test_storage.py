import io
from unittest.mock import patch

from tests.conftest import get_client


# noinspection PyUnusedLocal
@patch(
    "src.storage.service.upload_file_to_minio",
    return_value="https://fake-url.com/file.jpg",
)
def test_upload_file(mock_upload):
    client = get_client()
    file_content = b"fake image data"
    response = client.post(
        "/files/upload",
        files={"file": ("test.jpg", io.BytesIO(file_content), "image/jpeg")},
    )
    assert response.status_code == 200
    assert response.json() == {"file_url": "https://fake-url.com/file.jpg"}
