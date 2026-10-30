# payfound_sdk.CustomPOSConnectorApi

All URIs are relative to *http://127.0.0.1:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**connect_api_merchant_pos_plugin_connections_post**](CustomPOSConnectorApi.md#connect_api_merchant_pos_plugin_connections_post) | **POST** /api/merchant/pos-plugin/connections | Connect
[**disconnect_api_merchant_pos_plugin_connection_id_delete**](CustomPOSConnectorApi.md#disconnect_api_merchant_pos_plugin_connection_id_delete) | **DELETE** /api/merchant/pos-plugin/{connection_id} | Disconnect
[**overview_api_merchant_pos_plugin_get**](CustomPOSConnectorApi.md#overview_api_merchant_pos_plugin_get) | **GET** /api/merchant/pos-plugin | Overview
[**receive_api_pos_plugin_connection_id_events_post**](CustomPOSConnectorApi.md#receive_api_pos_plugin_connection_id_events_post) | **POST** /api/pos-plugin/{connection_id}/events | Receive
[**runs_api_merchant_pos_plugin_connection_id_runs_get**](CustomPOSConnectorApi.md#runs_api_merchant_pos_plugin_connection_id_runs_get) | **GET** /api/merchant/pos-plugin/{connection_id}/runs | Runs
[**sync_now_api_merchant_pos_plugin_connection_id_sync_post**](CustomPOSConnectorApi.md#sync_now_api_merchant_pos_plugin_connection_id_sync_post) | **POST** /api/merchant/pos-plugin/{connection_id}/sync | Sync Now
[**test_api_merchant_pos_plugin_connection_id_test_post**](CustomPOSConnectorApi.md#test_api_merchant_pos_plugin_connection_id_test_post) | **POST** /api/merchant/pos-plugin/{connection_id}/test | Test
[**update_api_merchant_pos_plugin_connection_id_patch**](CustomPOSConnectorApi.md#update_api_merchant_pos_plugin_connection_id_patch) | **PATCH** /api/merchant/pos-plugin/{connection_id} | Update


# **connect_api_merchant_pos_plugin_connections_post**
> object connect_api_merchant_pos_plugin_connections_post(app_pos_plugin_routes_connect_input, authorization=authorization, x_demo_role=x_demo_role)

Connect

### Example

* Api Key Authentication (demoRole):
* Bearer Authentication (bearerAuth):

```python
import payfound_sdk
from payfound_sdk.models.app_pos_plugin_routes_connect_input import AppPosPluginRoutesConnectInput
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
    api_instance = payfound_sdk.CustomPOSConnectorApi(api_client)
    app_pos_plugin_routes_connect_input = payfound_sdk.AppPosPluginRoutesConnectInput() # AppPosPluginRoutesConnectInput | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Connect
        api_response = api_instance.connect_api_merchant_pos_plugin_connections_post(app_pos_plugin_routes_connect_input, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of CustomPOSConnectorApi->connect_api_merchant_pos_plugin_connections_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomPOSConnectorApi->connect_api_merchant_pos_plugin_connections_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_pos_plugin_routes_connect_input** | [**AppPosPluginRoutesConnectInput**](AppPosPluginRoutesConnectInput.md)|  | 
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
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **disconnect_api_merchant_pos_plugin_connection_id_delete**
> object disconnect_api_merchant_pos_plugin_connection_id_delete(connection_id, authorization=authorization, x_demo_role=x_demo_role)

Disconnect

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
    api_instance = payfound_sdk.CustomPOSConnectorApi(api_client)
    connection_id = 'connection_id_example' # str | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Disconnect
        api_response = api_instance.disconnect_api_merchant_pos_plugin_connection_id_delete(connection_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of CustomPOSConnectorApi->disconnect_api_merchant_pos_plugin_connection_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomPOSConnectorApi->disconnect_api_merchant_pos_plugin_connection_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **connection_id** | **str**|  | 
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

# **overview_api_merchant_pos_plugin_get**
> object overview_api_merchant_pos_plugin_get(merchant_id, authorization=authorization, x_demo_role=x_demo_role)

Overview

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
    api_instance = payfound_sdk.CustomPOSConnectorApi(api_client)
    merchant_id = 'merchant_id_example' # str | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Overview
        api_response = api_instance.overview_api_merchant_pos_plugin_get(merchant_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of CustomPOSConnectorApi->overview_api_merchant_pos_plugin_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomPOSConnectorApi->overview_api_merchant_pos_plugin_get: %s\n" % e)
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

# **receive_api_pos_plugin_connection_id_events_post**
> object receive_api_pos_plugin_connection_id_events_post(connection_id)

Receive

Signed push. Headers: X-PayFound-Timestamp (unix seconds), X-PayFound-Signature (sha256=hex of
HMAC-SHA256(secret, timestamp + '.' + raw body)).

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
    api_instance = payfound_sdk.CustomPOSConnectorApi(api_client)
    connection_id = 'connection_id_example' # str | 

    try:
        # Receive
        api_response = api_instance.receive_api_pos_plugin_connection_id_events_post(connection_id)
        print("The response of CustomPOSConnectorApi->receive_api_pos_plugin_connection_id_events_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomPOSConnectorApi->receive_api_pos_plugin_connection_id_events_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
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

# **runs_api_merchant_pos_plugin_connection_id_runs_get**
> object runs_api_merchant_pos_plugin_connection_id_runs_get(connection_id, authorization=authorization, x_demo_role=x_demo_role)

Runs

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
    api_instance = payfound_sdk.CustomPOSConnectorApi(api_client)
    connection_id = 'connection_id_example' # str | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Runs
        api_response = api_instance.runs_api_merchant_pos_plugin_connection_id_runs_get(connection_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of CustomPOSConnectorApi->runs_api_merchant_pos_plugin_connection_id_runs_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomPOSConnectorApi->runs_api_merchant_pos_plugin_connection_id_runs_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **connection_id** | **str**|  | 
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

# **sync_now_api_merchant_pos_plugin_connection_id_sync_post**
> object sync_now_api_merchant_pos_plugin_connection_id_sync_post(connection_id, authorization=authorization, x_demo_role=x_demo_role)

Sync Now

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
    api_instance = payfound_sdk.CustomPOSConnectorApi(api_client)
    connection_id = 'connection_id_example' # str | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Sync Now
        api_response = api_instance.sync_now_api_merchant_pos_plugin_connection_id_sync_post(connection_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of CustomPOSConnectorApi->sync_now_api_merchant_pos_plugin_connection_id_sync_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomPOSConnectorApi->sync_now_api_merchant_pos_plugin_connection_id_sync_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **connection_id** | **str**|  | 
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

# **test_api_merchant_pos_plugin_connection_id_test_post**
> object test_api_merchant_pos_plugin_connection_id_test_post(connection_id, authorization=authorization, x_demo_role=x_demo_role)

Test

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
    api_instance = payfound_sdk.CustomPOSConnectorApi(api_client)
    connection_id = 'connection_id_example' # str | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Test
        api_response = api_instance.test_api_merchant_pos_plugin_connection_id_test_post(connection_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of CustomPOSConnectorApi->test_api_merchant_pos_plugin_connection_id_test_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomPOSConnectorApi->test_api_merchant_pos_plugin_connection_id_test_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **connection_id** | **str**|  | 
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

# **update_api_merchant_pos_plugin_connection_id_patch**
> object update_api_merchant_pos_plugin_connection_id_patch(connection_id, update_input, authorization=authorization, x_demo_role=x_demo_role)

Update

### Example

* Api Key Authentication (demoRole):
* Bearer Authentication (bearerAuth):

```python
import payfound_sdk
from payfound_sdk.models.update_input import UpdateInput
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
    api_instance = payfound_sdk.CustomPOSConnectorApi(api_client)
    connection_id = 'connection_id_example' # str | 
    update_input = payfound_sdk.UpdateInput() # UpdateInput | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Update
        api_response = api_instance.update_api_merchant_pos_plugin_connection_id_patch(connection_id, update_input, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of CustomPOSConnectorApi->update_api_merchant_pos_plugin_connection_id_patch:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CustomPOSConnectorApi->update_api_merchant_pos_plugin_connection_id_patch: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **connection_id** | **str**|  | 
 **update_input** | [**UpdateInput**](UpdateInput.md)|  | 
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

