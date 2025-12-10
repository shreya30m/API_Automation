from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.data_loader import load_payload
from utils.request_info import get_request_info
from utils.config import tenantId
import pytest
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.mark.order(15)
@pytest.mark.boundary
def test_boundary_relationship_search():
    """Test searching boundary relationships"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Read hierarchy type
    with open("output/ids.txt", "r") as f:
        for line in f:
            if line.startswith("Hierarchy Type:"):
                hierarchy_type = line.split(":")[1].strip()
                break

    # Load and prepare payload
    payload = load_payload("boundary_relationships", "search_relationships.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["BoundaryRelationshipSearchCriteria"]["tenantId"] = tenantId
    payload["BoundaryRelationshipSearchCriteria"]["hierarchyType"] = hierarchy_type

    # Make API call with includeChildren=true
    url = f"/boundary-service/boundary-relationships/_search?tenantId={tenantId}&includeChildren=true&hierarchyType={hierarchy_type}"
    response = client.post(url, payload)

    assert response.status_code == 200, f"Boundary relationship search failed: {response.text}"

    data = response.json()
    assert "TenantBoundary" in data

    # Log response details
    logger.info("="*80)
    logger.info("TEST 15 - BOUNDARY RELATIONSHIP SEARCH - RESPONSE")
    logger.info("="*80)
    logger.info(f"Status Code: {response.status_code}")
    logger.info(f"Response Data:\n{json.dumps(data, indent=2)}")
    logger.info("="*80)

    if data["TenantBoundary"] and len(data["TenantBoundary"]) > 0:
        boundary_count = len(data["TenantBoundary"][0].get("boundary", []))
        print(f"Boundary relationships found: {boundary_count} boundaries")
    else:
        print("No boundary relationships found yet")
