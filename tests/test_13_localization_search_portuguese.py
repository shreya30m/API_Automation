from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.data_loader import load_payload
from utils.request_info import get_request_info
from utils.config import tenantId, locale_portuguese
import pytest


@pytest.mark.order(13)
@pytest.mark.localization
def test_localization_search_portuguese():
    """Test searching Portuguese localization messages"""
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

    # Make API call with Portuguese locale
    url = f"/localization/messages/v1/_search?tenantId={tenantId}&locale={locale_portuguese}&module=hcm-boundary-{hierarchy_type_lower}"
    response = client.post(url, payload)

    assert response.status_code == 200, f"Portuguese localization search failed: {response.text}"

    data = response.json()
    assert "messages" in data

    print(f"Portuguese localization messages found: {len(data['messages'])} messages")
