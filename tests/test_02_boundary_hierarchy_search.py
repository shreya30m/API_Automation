from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.data_loader import load_payload
from utils.request_info import get_request_info
from utils.config import tenantId
import pytest


@pytest.mark.order(2)
@pytest.mark.boundary
def test_boundary_hierarchy_search():
    """Test searching for boundary hierarchy"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Read hierarchy type from previous test
    with open("output/ids.txt", "r") as f:
        for line in f:
            if line.startswith("Hierarchy Type:"):
                hierarchy_type = line.split(":")[1].strip()
                break

    # Load and prepare payload
    payload = load_payload("boundary_hierarchy", "search_hierarchy.json")
    payload["RequestInfo"] = get_request_info(token)
    payload["BoundaryTypeHierarchySearchCriteria"]["tenantId"] = tenantId
    payload["BoundaryTypeHierarchySearchCriteria"]["hierarchyType"] = hierarchy_type

    # Make API call
    response = client.post("/boundary-service/boundary-hierarchy-definition/_search?limit=10&offset=0", payload)

    assert response.status_code == 200, f"Boundary hierarchy search failed: {response.text}"

    data = response.json()
    assert "BoundaryHierarchy" in data
    assert len(data["BoundaryHierarchy"]) > 0
    assert data["BoundaryHierarchy"][0]["hierarchyType"] == hierarchy_type

    print(f"Boundary hierarchy found: {hierarchy_type}")
