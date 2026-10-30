# payfound_sdk.SuggestionsAndPriceWatchesApi

All URIs are relative to *http://127.0.0.1:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**competitor_prices_api_merchants_merchant_id_competitor_prices_get**](SuggestionsAndPriceWatchesApi.md#competitor_prices_api_merchants_merchant_id_competitor_prices_get) | **GET** /api/merchants/{merchant_id}/competitor-prices | Competitor Prices
[**create_price_watch_api_me_price_watches_post**](SuggestionsAndPriceWatchesApi.md#create_price_watch_api_me_price_watches_post) | **POST** /api/me/price-watches | Create Price Watch
[**delete_price_watch_api_me_price_watches_watch_id_delete**](SuggestionsAndPriceWatchesApi.md#delete_price_watch_api_me_price_watches_watch_id_delete) | **DELETE** /api/me/price-watches/{watch_id} | Delete Price Watch
[**list_price_watches_api_me_price_watches_get**](SuggestionsAndPriceWatchesApi.md#list_price_watches_api_me_price_watches_get) | **GET** /api/me/price-watches | List Price Watches
[**pickup_suggestions_api_pickup_suggestions_get**](SuggestionsAndPriceWatchesApi.md#pickup_suggestions_api_pickup_suggestions_get) | **GET** /api/pickup-suggestions | Pickup Suggestions
[**stock_up_api_merchants_merchant_id_stock_up_post**](SuggestionsAndPriceWatchesApi.md#stock_up_api_merchants_merchant_id_stock_up_post) | **POST** /api/merchants/{merchant_id}/stock-up | Stock Up


# **competitor_prices_api_merchants_merchant_id_competitor_prices_get**
> object competitor_prices_api_merchants_merchant_id_competitor_prices_get(merchant_id, authorization=authorization, x_demo_role=x_demo_role)

Competitor Prices

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
    api_instance = payfound_sdk.SuggestionsAndPriceWatchesApi(api_client)
    merchant_id = 'merchant_id_example' # str | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Competitor Prices
        api_response = api_instance.competitor_prices_api_merchants_merchant_id_competitor_prices_get(merchant_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of SuggestionsAndPriceWatchesApi->competitor_prices_api_merchants_merchant_id_competitor_prices_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SuggestionsAndPriceWatchesApi->competitor_prices_api_merchants_merchant_id_competitor_prices_get: %s\n" % e)
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

# **create_price_watch_api_me_price_watches_post**
> object create_price_watch_api_me_price_watches_post(watch_input, authorization=authorization, x_demo_role=x_demo_role)

Create Price Watch

### Example

* Api Key Authentication (demoRole):
* Bearer Authentication (bearerAuth):

```python
import payfound_sdk
from payfound_sdk.models.watch_input import WatchInput
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
    api_instance = payfound_sdk.SuggestionsAndPriceWatchesApi(api_client)
    watch_input = payfound_sdk.WatchInput() # WatchInput | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Create Price Watch
        api_response = api_instance.create_price_watch_api_me_price_watches_post(watch_input, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of SuggestionsAndPriceWatchesApi->create_price_watch_api_me_price_watches_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SuggestionsAndPriceWatchesApi->create_price_watch_api_me_price_watches_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **watch_input** | [**WatchInput**](WatchInput.md)|  | 
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

# **delete_price_watch_api_me_price_watches_watch_id_delete**
> delete_price_watch_api_me_price_watches_watch_id_delete(watch_id, authorization=authorization, x_demo_role=x_demo_role)

Delete Price Watch

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
    api_instance = payfound_sdk.SuggestionsAndPriceWatchesApi(api_client)
    watch_id = 'watch_id_example' # str | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Delete Price Watch
        api_instance.delete_price_watch_api_me_price_watches_watch_id_delete(watch_id, authorization=authorization, x_demo_role=x_demo_role)
    except Exception as e:
        print("Exception when calling SuggestionsAndPriceWatchesApi->delete_price_watch_api_me_price_watches_watch_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **watch_id** | **str**|  | 
 **authorization** | **str**|  | [optional] 
 **x_demo_role** | **str**|  | [optional] 

### Return type

void (empty response body)

### Authorization

[demoRole](../README.md#demoRole), [bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_price_watches_api_me_price_watches_get**
> object list_price_watches_api_me_price_watches_get(authorization=authorization, x_demo_role=x_demo_role)

List Price Watches

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
    api_instance = payfound_sdk.SuggestionsAndPriceWatchesApi(api_client)
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # List Price Watches
        api_response = api_instance.list_price_watches_api_me_price_watches_get(authorization=authorization, x_demo_role=x_demo_role)
        print("The response of SuggestionsAndPriceWatchesApi->list_price_watches_api_me_price_watches_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SuggestionsAndPriceWatchesApi->list_price_watches_api_me_price_watches_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
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

# **pickup_suggestions_api_pickup_suggestions_get**
> object pickup_suggestions_api_pickup_suggestions_get(merchant_id, day, authorization=authorization, x_demo_role=x_demo_role)

Pickup Suggestions

Top 5 pickup slots with room left on `day` (the store's local day, per branch timezone).

queue_estimate_minutes = round(booked / max(capacity, 1) * 10). It is a simple estimate from the share of the slot
already booked, not a measured wait time. Slots are ordered by booked share (emptiest first), then start time.

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
    api_instance = payfound_sdk.SuggestionsAndPriceWatchesApi(api_client)
    merchant_id = 'merchant_id_example' # str | 
    day = '2013-10-20' # date | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Pickup Suggestions
        api_response = api_instance.pickup_suggestions_api_pickup_suggestions_get(merchant_id, day, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of SuggestionsAndPriceWatchesApi->pickup_suggestions_api_pickup_suggestions_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SuggestionsAndPriceWatchesApi->pickup_suggestions_api_pickup_suggestions_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **merchant_id** | **str**|  | 
 **day** | **date**|  | 
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

# **stock_up_api_merchants_merchant_id_stock_up_post**
> object stock_up_api_merchants_merchant_id_stock_up_post(merchant_id, authorization=authorization, x_demo_role=x_demo_role, stock_up_body=stock_up_body)

Stock Up

Projects demand for the next `days` days and drafts (never sends) a supplier email for products that will sell out.

### Example

* Api Key Authentication (demoRole):
* Bearer Authentication (bearerAuth):

```python
import payfound_sdk
from payfound_sdk.models.stock_up_body import StockUpBody
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
    api_instance = payfound_sdk.SuggestionsAndPriceWatchesApi(api_client)
    merchant_id = 'merchant_id_example' # str | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)
    stock_up_body = payfound_sdk.StockUpBody() # StockUpBody |  (optional)

    try:
        # Stock Up
        api_response = api_instance.stock_up_api_merchants_merchant_id_stock_up_post(merchant_id, authorization=authorization, x_demo_role=x_demo_role, stock_up_body=stock_up_body)
        print("The response of SuggestionsAndPriceWatchesApi->stock_up_api_merchants_merchant_id_stock_up_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SuggestionsAndPriceWatchesApi->stock_up_api_merchants_merchant_id_stock_up_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **merchant_id** | **str**|  | 
 **authorization** | **str**|  | [optional] 
 **x_demo_role** | **str**|  | [optional] 
 **stock_up_body** | [**StockUpBody**](StockUpBody.md)|  | [optional] 

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

