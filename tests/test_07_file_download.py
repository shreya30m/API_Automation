from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.config import tenantId
import pytest


@pytest.mark.order(7)
@pytest.mark.file_operations
def test_file_download():
    """Test downloading generated file"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Read file store ID
    file_store_id = None
    with open("output/ids.txt", "r") as f:
        for line in f:
            if line.startswith("Generated FileStore ID:"):
                file_store_id = line.split(":")[1].strip()
                break

    if not file_store_id:
        pytest.skip("No generated file store ID found")

    # Make API call
    url = f"/filestore/v1/files/url?tenantId={tenantId}&fileStoreIds={file_store_id}"
    response = client.get(url)

    assert response.status_code == 200, f"File download URL retrieval failed: {response.text}"

    data = response.json()
    assert "fileStoreIds" in data
    assert len(data["fileStoreIds"]) > 0

    download_url = data["fileStoreIds"][0]["url"]
    print(f"File download URL retrieved: {download_url[:100]}...")
