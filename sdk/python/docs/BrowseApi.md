# payfound_sdk.BrowseApi

All URIs are relative to *http://127.0.0.1:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**browse_api_browse_get**](BrowseApi.md#browse_api_browse_get) | **GET** /api/browse | Browse


# **browse_api_browse_get**
> object browse_api_browse_get(q=q, mode=mode, latitude=latitude, longitude=longitude, radius_km=radius_km, limit=limit, authorization=authorization, x_demo_role=x_demo_role)

Browse

Read-only. Local products (real stock, distance) and online offers are returned in separate sections.

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
    api_instance = payfound_sdk.BrowseApi(api_client)
    q = '' # str |  (optional) (default to '')
    mode = 'both' # str |  (optional) (default to 'both')
    latitude = 3.4 # float |  (optional)
    longitude = 3.4 # float |  (optional)
    radius_km = 100 # float |  (optional) (default to 100)
    limit = 40 # int |  (optional) (default to 40)
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Browse
        api_response = api_instance.browse_api_browse_get(q=q, mode=mode, latitude=latitude, longitude=longitude, radius_km=radius_km, limit=limit, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of BrowseApi->browse_api_browse_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BrowseApi->browse_api_browse_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **q** | **str**|  | [optional] [default to &#39;&#39;]
 **mode** | **str**|  | [optional] [default to &#39;both&#39;]
 **latitude** | **float**|  | [optional] 
 **longitude** | **float**|  | [optional] 
 **radius_km** | **float**|  | [optional] [default to 100]
 **limit** | **int**|  | [optional] [default to 40]
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

