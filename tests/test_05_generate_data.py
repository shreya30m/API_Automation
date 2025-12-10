from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.data_loader import load_payload
from utils.request_info import get_request_info
from utils.config import tenantId
import pytest


@pytest.mark.order(5)
@pytest.mark.generate
def test_generate_data():
    """Test generating boundary data"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Read hierarchy type
    with open("output/ids.txt", "r") as f:
        for line in f:
            if line.startswith("Hierarchy Type:"):
                hierarchy_type = line.split(":")[1].strip()
                break

    # Load and prepare payload
    payload = load_payload("boundary_management", "generate_data.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["RequestInfo"]["userInfo"]["tenantId"] = tenantId

    # Make API call
    url = f"/boundary-management/v1/_generate?tenantId={tenantId}&forceUpdate=true&hierarchyType={hierarchy_type}"
    response = client.post(url, payload)

    assert response.status_code == 200, f"Generate data failed: {response.text}"

    data = response.json()
    assert "ResourceDetails" in data

    # Handle both list and dict response formats
    resource_details = data["ResourceDetails"]
    if isinstance(resource_details, list):
        generate_id = resource_details[0]["id"]
    else:
        generate_id = resource_details["id"]

    print(f"Boundary data generation triggered: {generate_id}")

    # Update generate ID (overwrite existing)
    with open("output/ids.txt", "r") as f:
        lines = f.readlines()

    with open("output/ids.txt", "w") as f:
        for line in lines:
            if line.startswith("Generate ID:"):
                f.write(f"Generate ID: {generate_id}\n")
            else:
                f.write(line)
        # Add Generate ID if not found
        if not any(line.startswith("Generate ID:") for line in lines):
            f.write(f"Generate ID: {generate_id}\n")
