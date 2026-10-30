# payfound_sdk.OnlineApi

All URIs are relative to *http://127.0.0.1:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**online_product_api_online_products_product_id_get**](OnlineApi.md#online_product_api_online_products_product_id_get) | **GET** /api/online/products/{product_id} | Online Product
[**online_search_api_online_search_get**](OnlineApi.md#online_search_api_online_search_get) | **GET** /api/online/search | Online Search


# **online_product_api_online_products_product_id_get**
> object online_product_api_online_products_product_id_get(product_id, authorization=authorization, x_demo_role=x_demo_role)

Online Product

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
    api_instance = payfound_sdk.OnlineApi(api_client)
    product_id = 'product_id_example' # str | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Online Product
        api_response = api_instance.online_product_api_online_products_product_id_get(product_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of OnlineApi->online_product_api_online_products_product_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OnlineApi->online_product_api_online_products_product_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **product_id** | **str**|  | 
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

# **online_search_api_online_search_get**
> object online_search_api_online_search_get(q, page_token=page_token, authorization=authorization, x_demo_role=x_demo_role)

Online Search

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
    api_instance = payfound_sdk.OnlineApi(api_client)
    q = 'q_example' # str | 
    page_token = 'page_token_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Online Search
        api_response = api_instance.online_search_api_online_search_get(q, page_token=page_token, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of OnlineApi->online_search_api_online_search_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OnlineApi->online_search_api_online_search_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **q** | **str**|  | 
 **page_token** | **str**|  | [optional] 
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

