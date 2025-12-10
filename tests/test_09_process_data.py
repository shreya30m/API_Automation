from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.data_loader import load_payload
from utils.request_info import get_request_info
from utils.config import tenantId
import pytest


@pytest.mark.order(9)
@pytest.mark.process
def test_process_data():
    """Test processing uploaded boundary data"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Read required IDs
    hierarchy_type = None
    file_store_id = None

    with open("output/ids.txt", "r") as f:
        for line in f:
            if line.startswith("Hierarchy Type:"):
                hierarchy_type = line.split(":")[1].strip()
            elif line.startswith("Uploaded FileStore ID:"):
                file_store_id = line.split(":")[1].strip()

    if not hierarchy_type or not file_store_id:
        pytest.skip("Missing required IDs (hierarchy type or file store ID)")

    # Load and prepare payload
    payload = load_payload("boundary_management", "process_data.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["RequestInfo"]["userInfo"]["tenantId"] = tenantId
    payload["ResourceDetails"]["tenantId"] = tenantId
    payload["ResourceDetails"]["fileStoreId"] = file_store_id
    payload["ResourceDetails"]["hierarchyType"] = hierarchy_type

    # Make API call
    response = client.post("/boundary-management/v1/_process", payload)

    assert response.status_code == 200, f"Process data failed: {response.text}"

    data = response.json()
    assert "ResourceDetails" in data

    # Handle both list and dict response formats
    resource_details = data["ResourceDetails"]
    if isinstance(resource_details, list):
        process_id = resource_details[0]["id"]
    else:
        process_id = resource_details["id"]

    print(f"Boundary data processing triggered: {process_id}")

    # Update process ID (overwrite existing)
    with open("output/ids.txt", "r") as f:
        lines = f.readlines()

    with open("output/ids.txt", "w") as f:
        for line in lines:
            if line.startswith("Process ID:"):
                f.write(f"Process ID: {process_id}\n")
            else:
                f.write(line)
        # Add if not found
        if not any(line.startswith("Process ID:") for line in lines):
            f.write(f"Process ID: {process_id}\n")
