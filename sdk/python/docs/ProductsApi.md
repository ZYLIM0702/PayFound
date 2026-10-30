# payfound_sdk.ProductsApi

All URIs are relative to *http://127.0.0.1:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**product_detail_api_products_product_id_get**](ProductsApi.md#product_detail_api_products_product_id_get) | **GET** /api/products/{product_id} | Product Detail
[**products_api_products_get**](ProductsApi.md#products_api_products_get) | **GET** /api/products | Products


# **product_detail_api_products_product_id_get**
> object product_detail_api_products_product_id_get(product_id, latitude=latitude, longitude=longitude)

Product Detail

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
    api_instance = payfound_sdk.ProductsApi(api_client)
    product_id = 'product_id_example' # str | 
    latitude = 3.4 # float |  (optional)
    longitude = 3.4 # float |  (optional)

    try:
        # Product Detail
        api_response = api_instance.product_detail_api_products_product_id_get(product_id, latitude=latitude, longitude=longitude)
        print("The response of ProductsApi->product_detail_api_products_product_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProductsApi->product_detail_api_products_product_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **product_id** | **str**|  | 
 **latitude** | **float**|  | [optional] 
 **longitude** | **float**|  | [optional] 

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

# **products_api_products_get**
> object products_api_products_get(q=q, category=category, merchant_id=merchant_id, latitude=latitude, longitude=longitude, radius_km=radius_km, open_now=open_now, in_stock=in_stock, location_id=location_id, ids=ids, limit=limit, offset=offset)

Products

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
    api_instance = payfound_sdk.ProductsApi(api_client)
    q = '' # str |  (optional) (default to '')
    category = '' # str |  (optional) (default to '')
    merchant_id = '' # str |  (optional) (default to '')
    latitude = 3.4 # float |  (optional)
    longitude = 3.4 # float |  (optional)
    radius_km = 100 # float |  (optional) (default to 100)
    open_now = False # bool |  (optional) (default to False)
    in_stock = False # bool |  (optional) (default to False)
    location_id = 'location_id_example' # str |  (optional)
    ids = '' # str |  (optional) (default to '')
    limit = 400 # int |  (optional) (default to 400)
    offset = 0 # int |  (optional) (default to 0)

    try:
        # Products
        api_response = api_instance.products_api_products_get(q=q, category=category, merchant_id=merchant_id, latitude=latitude, longitude=longitude, radius_km=radius_km, open_now=open_now, in_stock=in_stock, location_id=location_id, ids=ids, limit=limit, offset=offset)
        print("The response of ProductsApi->products_api_products_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProductsApi->products_api_products_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **q** | **str**|  | [optional] [default to &#39;&#39;]
 **category** | **str**|  | [optional] [default to &#39;&#39;]
 **merchant_id** | **str**|  | [optional] [default to &#39;&#39;]
 **latitude** | **float**|  | [optional] 
 **longitude** | **float**|  | [optional] 
 **radius_km** | **float**|  | [optional] [default to 100]
 **open_now** | **bool**|  | [optional] [default to False]
 **in_stock** | **bool**|  | [optional] [default to False]
 **location_id** | **str**|  | [optional] 
 **ids** | **str**|  | [optional] [default to &#39;&#39;]
 **limit** | **int**|  | [optional] [default to 400]
 **offset** | **int**|  | [optional] [default to 0]

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

