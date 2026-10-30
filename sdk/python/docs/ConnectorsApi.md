# payfound_sdk.ConnectorsApi

All URIs are relative to *http://127.0.0.1:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**native_checkout_api_connectors_connection_id_checkout_get**](ConnectorsApi.md#native_checkout_api_connectors_connection_id_checkout_get) | **GET** /api/connectors/{connection_id}/checkout | Native Checkout
[**receive_hook_api_connectors_provider_connection_id_webhook_post**](ConnectorsApi.md#receive_hook_api_connectors_provider_connection_id_webhook_post) | **POST** /api/connectors/{provider}/{connection_id}/webhook | Receive Hook
[**shopify_callback_api_connectors_shopify_callback_get**](ConnectorsApi.md#shopify_callback_api_connectors_shopify_callback_get) | **GET** /api/connectors/shopify/callback | Shopify Callback


# **native_checkout_api_connectors_connection_id_checkout_get**
> object native_checkout_api_connectors_connection_id_checkout_get(connection_id, product_id)

Native Checkout

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
    api_instance = payfound_sdk.ConnectorsApi(api_client)
    connection_id = 'connection_id_example' # str | 
    product_id = 'product_id_example' # str | 

    try:
        # Native Checkout
        api_response = api_instance.native_checkout_api_connectors_connection_id_checkout_get(connection_id, product_id)
        print("The response of ConnectorsApi->native_checkout_api_connectors_connection_id_checkout_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConnectorsApi->native_checkout_api_connectors_connection_id_checkout_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **connection_id** | **str**|  | 
 **product_id** | **str**|  | 

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

# **receive_hook_api_connectors_provider_connection_id_webhook_post**
> object receive_hook_api_connectors_provider_connection_id_webhook_post(provider, connection_id)

Receive Hook

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
    api_instance = payfound_sdk.ConnectorsApi(api_client)
    provider = 'provider_example' # str | 
    connection_id = 'connection_id_example' # str | 

    try:
        # Receive Hook
        api_response = api_instance.receive_hook_api_connectors_provider_connection_id_webhook_post(provider, connection_id)
        print("The response of ConnectorsApi->receive_hook_api_connectors_provider_connection_id_webhook_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConnectorsApi->receive_hook_api_connectors_provider_connection_id_webhook_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **provider** | **str**|  | 
 **connection_id** | **str**|  | 

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

# **shopify_callback_api_connectors_shopify_callback_get**
> object shopify_callback_api_connectors_shopify_callback_get()

Shopify Callback

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
    api_instance = payfound_sdk.ConnectorsApi(api_client)

    try:
        # Shopify Callback
        api_response = api_instance.shopify_callback_api_connectors_shopify_callback_get()
        print("The response of ConnectorsApi->shopify_callback_api_connectors_shopify_callback_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConnectorsApi->shopify_callback_api_connectors_shopify_callback_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

