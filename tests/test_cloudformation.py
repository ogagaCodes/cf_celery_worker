import pytest
from unittest.mock import patch, MagicMock
from app.cloudformation import create_and_deploy_cloudformation, create_cloudformation_template

@pytest.fixture
def mock_boto_client():
    # Mock the boto3 client for CloudFormation
    with patch("app.cloudformation.boto3.client") as mock_client:
        mock_cf_client = MagicMock()
        mock_client.return_value = mock_cf_client
        yield mock_cf_client

def test_create_cloudformation_template():
    worker_count = 3
    # Call the function to generate the CloudFormation template
    template_body = create_cloudformation_template(worker_count)
    
    # Ensure the template is a non-empty string (you can perform more specific checks as needed)
    assert isinstance(template_body, str)
    assert len(template_body) > 0

def test_create_and_deploy_cloudformation(mock_boto_client):
    # Given
    worker_count = 3
    mock_boto_client.create_stack.return_value = {
        "StackId": "arn:aws:cloudformation:us-east-1:123456789012:stack/CeleryWorkerStack/stack-id"
    }

    # When
    response = create_and_deploy_cloudformation(worker_count)

    # Then
    # Check if create_stack was called with the correct arguments
    mock_boto_client.create_stack.assert_called_once()
    
    # Verify that the response contains the correct StackId
    assert "StackId" in response
    assert response["StackId"] == "arn:aws:cloudformation:us-east-1:123456789012:stack/CeleryWorkerStack/stack-id"

    # Verify that the worker count was correctly passed as a parameter
    args, kwargs = mock_boto_client.create_stack.call_args
    assert "WorkerCount" in [param["ParameterKey"] for param in kwargs["Parameters"]]
    assert any(param["ParameterValue"] == str(worker_count) for param in kwargs["Parameters"])

    # Ensure that the CAPABILITY_NAMED_IAM was set
    assert "CAPABILITY_NAMED_IAM" in kwargs["Capabilities"]
