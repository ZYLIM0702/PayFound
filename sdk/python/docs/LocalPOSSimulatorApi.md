# payfound_sdk.LocalPOSSimulatorApi

All URIs are relative to *http://127.0.0.1:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**connect_api_pos_simulator_connect_post**](LocalPOSSimulatorApi.md#connect_api_pos_simulator_connect_post) | **POST** /api/pos-simulator/connect | Connect
[**connection_api_pos_simulator_connection_patch**](LocalPOSSimulatorApi.md#connection_api_pos_simulator_connection_patch) | **PATCH** /api/pos-simulator/connection | Connection
[**sale_api_pos_simulator_sales_post**](LocalPOSSimulatorApi.md#sale_api_pos_simulator_sales_post) | **POST** /api/pos-simulator/sales | Sale
[**state_api_pos_simulator_state_get**](LocalPOSSimulatorApi.md#state_api_pos_simulator_state_get) | **GET** /api/pos-simulator/state | State
[**stock_count_api_pos_simulator_stock_count_post**](LocalPOSSimulatorApi.md#stock_count_api_pos_simulator_stock_count_post) | **POST** /api/pos-simulator/stock-count | Stock Count
[**synchronize_api_pos_simulator_sync_post**](LocalPOSSimulatorApi.md#synchronize_api_pos_simulator_sync_post) | **POST** /api/pos-simulator/sync | Synchronize


# **connect_api_pos_simulator_connect_post**
> object connect_api_pos_simulator_connect_post(merchant_id, authorization=authorization, x_demo_role=x_demo_role)

Connect

### Example

* Api Key Authentication (demoRole):
* Bearer Authentication (bearerAuth):

```python
import payfound_sdk
from payfound_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://127.0.0.1:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = payfound_sdk.Configuration(
    host = "http://127.0.0.1:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: demoRole
configuration.api_key['demoRole'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['demoRole'] = 'Bearer'

# Configure Bearer authorization: bearerAuth
configuration = payfound_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with payfound_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = payfound_sdk.LocalPOSSimulatorApi(api_client)
    merchant_id = 'merchant_id_example' # str | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Connect
        api_response = api_instance.connect_api_pos_simulator_connect_post(merchant_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of LocalPOSSimulatorApi->connect_api_pos_simulator_connect_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LocalPOSSimulatorApi->connect_api_pos_simulator_connect_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **merchant_id** | **str**|  | 
 **authorization** | **str**|  | [optional] 
 **x_demo_role** | **str**|  | [optional] 

### Return type

**object**

### Authorization

[demoRole](../README.md#demoRole), [bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **connection_api_pos_simulator_connection_patch**
> object connection_api_pos_simulator_connection_patch(merchant_id, connection_input, authorization=authorization, x_demo_role=x_demo_role)

Connection

### Example

* Api Key Authentication (demoRole):
* Bearer Authentication (bearerAuth):

```python
import payfound_sdk
from payfound_sdk.models.connection_input import ConnectionInput
from payfound_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://127.0.0.1:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = payfound_sdk.Configuration(
    host = "http://127.0.0.1:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: demoRole
configuration.api_key['demoRole'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['demoRole'] = 'Bearer'

# Configure Bearer authorization: bearerAuth
configuration = payfound_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with payfound_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = payfound_sdk.LocalPOSSimulatorApi(api_client)
    merchant_id = 'merchant_id_example' # str | 
    connection_input = payfound_sdk.ConnectionInput() # ConnectionInput | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Connection
        api_response = api_instance.connection_api_pos_simulator_connection_patch(merchant_id, connection_input, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of LocalPOSSimulatorApi->connection_api_pos_simulator_connection_patch:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LocalPOSSimulatorApi->connection_api_pos_simulator_connection_patch: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **merchant_id** | **str**|  | 
 **connection_input** | [**ConnectionInput**](ConnectionInput.md)|  | 
 **authorization** | **str**|  | [optional] 
 **x_demo_role** | **str**|  | [optional] 

### Return type

**object**

### Authorization

[demoRole](../README.md#demoRole), [bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **sale_api_pos_simulator_sales_post**
> object sale_api_pos_simulator_sales_post(merchant_id, sale_input, authorization=authorization, x_demo_role=x_demo_role)

Sale

### Example

* Api Key Authentication (demoRole):
* Bearer Authentication (bearerAuth):

```python
import payfound_sdk
from payfound_sdk.models.sale_input import SaleInput
from payfound_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://127.0.0.1:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = payfound_sdk.Configuration(
    host = "http://127.0.0.1:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: demoRole
configuration.api_key['demoRole'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['demoRole'] = 'Bearer'

# Configure Bearer authorization: bearerAuth
configuration = payfound_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with payfound_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = payfound_sdk.LocalPOSSimulatorApi(api_client)
    merchant_id = 'merchant_id_example' # str | 
    sale_input = payfound_sdk.SaleInput() # SaleInput | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Sale
        api_response = api_instance.sale_api_pos_simulator_sales_post(merchant_id, sale_input, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of LocalPOSSimulatorApi->sale_api_pos_simulator_sales_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LocalPOSSimulatorApi->sale_api_pos_simulator_sales_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **merchant_id** | **str**|  | 
 **sale_input** | [**SaleInput**](SaleInput.md)|  | 
 **authorization** | **str**|  | [optional] 
 **x_demo_role** | **str**|  | [optional] 

### Return type

**object**

### Authorization

[demoRole](../README.md#demoRole), [bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **state_api_pos_simulator_state_get**
> object state_api_pos_simulator_state_get(merchant_id, authorization=authorization, x_demo_role=x_demo_role)

State

### Example

* Api Key Authentication (demoRole):
* Bearer Authentication (bearerAuth):

```python
import payfound_sdk
from payfound_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://127.0.0.1:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = payfound_sdk.Configuration(
    host = "http://127.0.0.1:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: demoRole
configuration.api_key['demoRole'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['demoRole'] = 'Bearer'

# Configure Bearer authorization: bearerAuth
configuration = payfound_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with payfound_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = payfound_sdk.LocalPOSSimulatorApi(api_client)
    merchant_id = 'merchant_id_example' # str | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # State
        api_response = api_instance.state_api_pos_simulator_state_get(merchant_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of LocalPOSSimulatorApi->state_api_pos_simulator_state_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LocalPOSSimulatorApi->state_api_pos_simulator_state_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **merchant_id** | **str**|  | 
 **authorization** | **str**|  | [optional] 
 **x_demo_role** | **str**|  | [optional] 

### Return type

**object**

### Authorization

[demoRole](../README.md#demoRole), [bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **stock_count_api_pos_simulator_stock_count_post**
> object stock_count_api_pos_simulator_stock_count_post(merchant_id, stock_input, authorization=authorization, x_demo_role=x_demo_role)

Stock Count

### Example

* Api Key Authentication (demoRole):
* Bearer Authentication (bearerAuth):

```python
import payfound_sdk
from payfound_sdk.models.stock_input import StockInput
from payfound_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://127.0.0.1:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = payfound_sdk.Configuration(
    host = "http://127.0.0.1:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: demoRole
configuration.api_key['demoRole'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['demoRole'] = 'Bearer'

# Configure Bearer authorization: bearerAuth
configuration = payfound_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with payfound_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = payfound_sdk.LocalPOSSimulatorApi(api_client)
    merchant_id = 'merchant_id_example' # str | 
    stock_input = payfound_sdk.StockInput() # StockInput | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Stock Count
        api_response = api_instance.stock_count_api_pos_simulator_stock_count_post(merchant_id, stock_input, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of LocalPOSSimulatorApi->stock_count_api_pos_simulator_stock_count_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LocalPOSSimulatorApi->stock_count_api_pos_simulator_stock_count_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **merchant_id** | **str**|  | 
 **stock_input** | [**StockInput**](StockInput.md)|  | 
 **authorization** | **str**|  | [optional] 
 **x_demo_role** | **str**|  | [optional] 

### Return type

**object**

### Authorization

[demoRole](../README.md#demoRole), [bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **synchronize_api_pos_simulator_sync_post**
> object synchronize_api_pos_simulator_sync_post(merchant_id, authorization=authorization, x_demo_role=x_demo_role)

Synchronize

### Example

* Api Key Authentication (demoRole):
* Bearer Authentication (bearerAuth):

```python
import payfound_sdk
from payfound_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://127.0.0.1:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = payfound_sdk.Configuration(
    host = "http://127.0.0.1:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: demoRole
configuration.api_key['demoRole'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['demoRole'] = 'Bearer'

# Configure Bearer authorization: bearerAuth
configuration = payfound_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with payfound_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = payfound_sdk.LocalPOSSimulatorApi(api_client)
    merchant_id = 'merchant_id_example' # str | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Synchronize
        api_response = api_instance.synchronize_api_pos_simulator_sync_post(merchant_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of LocalPOSSimulatorApi->synchronize_api_pos_simulator_sync_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LocalPOSSimulatorApi->synchronize_api_pos_simulator_sync_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **merchant_id** | **str**|  | 
 **authorization** | **str**|  | [optional] 
 **x_demo_role** | **str**|  | [optional] 

### Return type

**object**

### Authorization

[demoRole](../README.md#demoRole), [bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

