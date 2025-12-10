from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.data_loader import load_payload
from utils.request_info import get_request_info
from utils.config import tenantId
import pytest


@pytest.mark.order(10)
@pytest.mark.process
def test_process_search():
    """Test searching for processed boundary data"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Read process ID
    process_id = None
    with open("output/ids.txt", "r") as f:
        for line in f:
            if line.startswith("Process ID:"):
                process_id = line.split(":")[1].strip()
                break

    if not process_id:
        pytest.skip("No process ID found")

    # Load and prepare payload
    payload = load_payload("boundary_management", "process_search.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["RequestInfo"]["userInfo"]["tenantId"] = tenantId
    payload["SearchCriteria"]["id"] = [process_id]
    payload["SearchCriteria"]["tenantId"] = tenantId

    # Make API call
    response = client.post("/boundary-management/v1/_process-search", payload)

    assert response.status_code == 200, f"Process search failed: {response.text}"

    data = response.json()
    assert "ResourceDetails" in data
    assert len(data["ResourceDetails"]) > 0

    status = data["ResourceDetails"][0]["status"]
    processed_filestore_id = data["ResourceDetails"][0].get("processedFilestoreId")

    print(f"Process status: {status}")

    if processed_filestore_id:
        print(f"Processed file store ID: {processed_filestore_id}")
        with open("output/ids.txt", "a") as f:
            f.write(f"Processed FileStore ID: {processed_filestore_id}\n")
