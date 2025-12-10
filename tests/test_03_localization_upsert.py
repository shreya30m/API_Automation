from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.data_loader import load_payload
from utils.request_info import get_request_info
from utils.config import tenantId, locale
import pytest


@pytest.mark.order(3)
@pytest.mark.localization
def test_localization_upsert():
    """Test upserting localization messages"""
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
    payload = load_payload("localization", "upsert_localization.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["tenantId"] = tenantId
    payload["messages"] = [
        {
            "code": f"{hierarchy_type}_COUNTRY",
            "message": "Country",
            "module": f"hcm-boundary-{hierarchy_type_lower}",
            "locale": locale
        },
        {
            "code": f"{hierarchy_type}_PROVINCE",
            "message": "Province",
            "module": f"hcm-boundary-{hierarchy_type_lower}",
            "locale": locale
        },
        {
            "code": f"{hierarchy_type}_DISTRICT",
            "message": "Distrito",
            "module": f"hcm-boundary-{hierarchy_type_lower}",
            "locale": locale
        },
        {
            "code": f"{hierarchy_type}_POST ADMINISTRATIVE",
            "message": "Post administrative",
            "module": f"hcm-boundary-{hierarchy_type_lower}",
            "locale": locale
        },
        {
            "code": f"{hierarchy_type}_LOCALITY",
            "message": "Locality",
            "module": f"hcm-boundary-{hierarchy_type_lower}",
            "locale": locale
        },
        {
            "code": f"{hierarchy_type}_VILLAGE",
            "message": "Village",
            "module": f"hcm-boundary-{hierarchy_type_lower}",
            "locale": locale
        }
    ]

    # Make API call
    response = client.post("/localization/messages/v1/_upsert", payload)

    assert response.status_code == 200, f"Localization upsert failed: {response.text}"

    data = response.json()
    assert "messages" in data
    assert len(data["messages"]) == 6

    print(f"Localization messages upserted successfully: {len(data['messages'])} messages")
