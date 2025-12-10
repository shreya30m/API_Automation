from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.data_loader import load_payload
from utils.request_info import get_request_info
from utils.config import tenantId
import pytest
import time


@pytest.mark.order(6)
@pytest.mark.generate
def test_generate_search():
    """Test searching for generated boundary data with polling"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Read hierarchy type
    with open("output/ids.txt", "r") as f:
        for line in f:
            if line.startswith("Hierarchy Type:"):
                hierarchy_type = line.split(":")[1].strip()
                break

    # Load and prepare payload
    payload = load_payload("boundary_management", "generate_search.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["RequestInfo"]["userInfo"]["tenantId"] = tenantId

    # Poll for file generation completion
    url = f"/boundary-management/v1/_generate-search?tenantId={tenantId}&hierarchyType={hierarchy_type}"
    max_attempts = 30  # 30 attempts
    wait_time = 2  # 2 seconds between attempts
    file_store_id = None

    print("Polling for file generation completion...")
    for attempt in range(max_attempts):
        response = client.post(url, payload)
        assert response.status_code == 200, f"Generate search failed: {response.text}"

        data = response.json()
        assert "GeneratedResource" in data

        if len(data["GeneratedResource"]) > 0:
            resource = data["GeneratedResource"][0]
            status = resource.get("status")
            file_store_id = resource.get("fileStoreid")  # lowercase 'id'

            print(f"Attempt {attempt + 1}/{max_attempts}: Status={status}, FileStoreId={'Found' if file_store_id else 'Not yet'}")

            if file_store_id and status == "completed":
                print(f"File generation completed! FileStore ID: {file_store_id}")
                break
            elif status == "failed":
                pytest.fail(f"File generation failed with status: {status}")

        if attempt < max_attempts - 1:
            time.sleep(wait_time)
    else:
        pytest.fail(f"File generation did not complete within {max_attempts * wait_time} seconds")

    # Save the file store ID
    with open("output/ids.txt", "r") as f:
        lines = f.readlines()

    with open("output/ids.txt", "w") as f:
        for line in lines:
            if line.startswith("Generated FileStore ID:"):
                f.write(f"Generated FileStore ID: {file_store_id}\n")
            else:
                f.write(line)
        # Add if not found
        if not any(line.startswith("Generated FileStore ID:") for line in lines):
            f.write(f"Generated FileStore ID: {file_store_id}\n")
