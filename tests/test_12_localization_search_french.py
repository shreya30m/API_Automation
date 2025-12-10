from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.data_loader import load_payload
from utils.request_info import get_request_info
from utils.config import tenantId, locale_french
import pytest


@pytest.mark.order(12)
@pytest.mark.localization
def test_localization_search_french():
    """Test searching French localization messages"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Read hierarchy type
    with open("output/ids.txt", "r") as f:
        for line in f:
            if line.startswith("Hierarchy Type:"):
                hierarchy_type = line.split(":")[1].strip()
                break

    hierarchy_type_lower = hierarchy_type.lower()

    # Load and prepare payload
    payload = load_payload("localization", "search_localization.json")
    payload["RequestInfo"] = get_request_info(token)

    # Make API call with French locale
    url = f"/localization/messages/v1/_search?tenantId={tenantId}&locale={locale_french}&module=hcm-boundary-{hierarchy_type_lower}"
    response = client.post(url, payload)

    assert response.status_code == 200, f"French localization search failed: {response.text}"

    data = response.json()
    assert "messages" in data

    print(f"French localization messages found: {len(data['messages'])} messages")
