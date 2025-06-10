import pytest
import botocore
from scan import api_call_with_retry

def test_api_call_success(mocker):
    """Test successful API call."""
    mock_client = mocker.MagicMock()
    mock_function = mocker.MagicMock(return_value={"Result": "Success"})
    mock_client.some_function = mock_function
    
    result = api_call_with_retry(mock_client, "some_function", None, 3, 1)()
    
    assert result == {"Result": "Success"}
    mock_function.assert_called_once()

def test_api_call_with_parameters(mocker):
    """Test API call with parameters."""
    mock_client = mocker.MagicMock()
    mock_function = mocker.MagicMock(return_value={"Result": "Success"})
    mock_client.some_function = mock_function
    params = {"Param1": "Value1"}
    
    result = api_call_with_retry(mock_client, "some_function", params, 3, 1)()
    
    mock_function.assert_called_once_with(Param1="Value1")
    assert result == {"Result": "Success"}

def test_api_call_throttling_retry(mocker):
    """Test API call retry on throttling."""
    mock_client = mocker.MagicMock()
    mock_function = mocker.MagicMock()
    mock_client.some_function = mock_function
    
    # First call raises throttling error, second succeeds
    throttling_error = botocore.exceptions.ClientError(
        {"Error": {"Code": "Throttling"}}, "operation_name"
    )
    mock_function.side_effect = [throttling_error, {"Result": "Success"}]
    
    result = api_call_with_retry(mock_client, "some_function", None, 3, 1)()
    
    assert mock_function.call_count == 2
    assert result == {"Result": "Success"}

def test_api_call_max_retries_exceeded(mocker):
    """Test API call with max retries exceeded."""
    mock_client = mocker.MagicMock()
    mock_function = mocker.MagicMock()
    mock_client.some_function = mock_function
    
    # All calls raise throttling error
    throttling_error = botocore.exceptions.ClientError(
        {"Error": {"Code": "Throttling"}}, "operation_name"
    )
    mock_function.side_effect = [throttling_error, throttling_error, throttling_error]
    
    result = api_call_with_retry(mock_client, "some_function", None, 3, 1)()
    
    assert mock_function.call_count == 3
    assert result is None

def test_api_call_non_throttling_error(mocker):
    """Test API call with non-throttling error."""
    mock_client = mocker.MagicMock()
    mock_function = mocker.MagicMock()
    mock_client.some_function = mock_function
    
    # Raise non-throttling error
    error = botocore.exceptions.ClientError(
        {"Error": {"Code": "AccessDenied"}}, "operation_name"
    )
    mock_function.side_effect = error
    
    with pytest.raises(botocore.exceptions.ClientError):
        api_call_with_retry(mock_client, "some_function", None, 3, 1)()