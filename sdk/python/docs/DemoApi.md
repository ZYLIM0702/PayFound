# payfound_sdk.DemoApi

All URIs are relative to *http://127.0.0.1:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**demo_ip_anchor_api_demo_ip_anchor_get**](DemoApi.md#demo_ip_anchor_api_demo_ip_anchor_get) | **GET** /api/demo/ip-anchor | Demo Ip Anchor
[**demo_placement_reset_api_demo_placement_reset_post**](DemoApi.md#demo_placement_reset_api_demo_placement_reset_post) | **POST** /api/demo/placement/reset | Demo Placement Reset
[**demo_placement_state_api_demo_placement_get**](DemoApi.md#demo_placement_state_api_demo_placement_get) | **GET** /api/demo/placement | Demo Placement State


# **demo_ip_anchor_api_demo_ip_anchor_get**
> object demo_ip_anchor_api_demo_ip_anchor_get()

Demo Ip Anchor

City-level default area from the caller's IP (2 dp, memory-cached, never stored). 204 when unknown.

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
    api_instance = payfound_sdk.DemoApi(api_client)

    try:
        # Demo Ip Anchor
        api_response = api_instance.demo_ip_anchor_api_demo_ip_anchor_get()
        print("The response of DemoApi->demo_ip_anchor_api_demo_ip_anchor_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DemoApi->demo_ip_anchor_api_demo_ip_anchor_get: %s\n" % e)
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

# **demo_placement_reset_api_demo_placement_reset_post**
> object demo_placement_reset_api_demo_placement_reset_post()

Demo Placement Reset

Demo-only, loopback-only: forget cached layouts (used to simulate a cold server).

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
    api_instance = payfound_sdk.DemoApi(api_client)

    try:
        # Demo Placement Reset
        api_response = api_instance.demo_placement_reset_api_demo_placement_reset_post()
        print("The response of DemoApi->demo_placement_reset_api_demo_placement_reset_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DemoApi->demo_placement_reset_api_demo_placement_reset_post: %s\n" % e)
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

# **demo_placement_state_api_demo_placement_get**
> object demo_placement_state_api_demo_placement_get()

Demo Placement State

How the demo stores are laid out for this viewer (relocated around the anchor, or the original San Francisco set).

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
    api_instance = payfound_sdk.DemoApi(api_client)

    try:
        # Demo Placement State
        api_response = api_instance.demo_placement_state_api_demo_placement_get()
        print("The response of DemoApi->demo_placement_state_api_demo_placement_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DemoApi->demo_placement_state_api_demo_placement_get: %s\n" % e)
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

