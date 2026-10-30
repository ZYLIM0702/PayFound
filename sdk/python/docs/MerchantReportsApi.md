# payfound_sdk.MerchantReportsApi

All URIs are relative to *http://127.0.0.1:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_card_api_merchant_report_cards_post**](MerchantReportsApi.md#create_card_api_merchant_report_cards_post) | **POST** /api/merchant/report-cards | Create Card
[**delete_card_api_merchant_report_cards_card_id_delete**](MerchantReportsApi.md#delete_card_api_merchant_report_cards_card_id_delete) | **DELETE** /api/merchant/report-cards/{card_id} | Delete Card
[**list_cards_api_merchant_report_cards_get**](MerchantReportsApi.md#list_cards_api_merchant_report_cards_get) | **GET** /api/merchant/report-cards | List Cards
[**open_card_api_merchant_report_cards_card_id_get**](MerchantReportsApi.md#open_card_api_merchant_report_cards_card_id_get) | **GET** /api/merchant/report-cards/{card_id} | Open Card
[**preview_api_merchant_report_cards_preview_get**](MerchantReportsApi.md#preview_api_merchant_report_cards_preview_get) | **GET** /api/merchant/report-cards/preview | Preview
[**report_pack_api_merchant_report_pack_get**](MerchantReportsApi.md#report_pack_api_merchant_report_pack_get) | **GET** /api/merchant/report-pack | Report Pack


# **create_card_api_merchant_report_cards_post**
> object create_card_api_merchant_report_cards_post(card_save, authorization=authorization, x_demo_role=x_demo_role)

Create Card

### Example

* Api Key Authentication (demoRole):
* Bearer Authentication (bearerAuth):

```python
import payfound_sdk
from payfound_sdk.models.card_save import CardSave
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
    api_instance = payfound_sdk.MerchantReportsApi(api_client)
    card_save = payfound_sdk.CardSave() # CardSave | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Create Card
        api_response = api_instance.create_card_api_merchant_report_cards_post(card_save, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantReportsApi->create_card_api_merchant_report_cards_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantReportsApi->create_card_api_merchant_report_cards_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **card_save** | [**CardSave**](CardSave.md)|  | 
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

# **delete_card_api_merchant_report_cards_card_id_delete**
> delete_card_api_merchant_report_cards_card_id_delete(card_id, authorization=authorization, x_demo_role=x_demo_role)

Delete Card

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
    api_instance = payfound_sdk.MerchantReportsApi(api_client)
    card_id = 'card_id_example' # str | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Delete Card
        api_instance.delete_card_api_merchant_report_cards_card_id_delete(card_id, authorization=authorization, x_demo_role=x_demo_role)
    except Exception as e:
        print("Exception when calling MerchantReportsApi->delete_card_api_merchant_report_cards_card_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **card_id** | **str**|  | 
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

# **list_cards_api_merchant_report_cards_get**
> object list_cards_api_merchant_report_cards_get(merchant_id, authorization=authorization, x_demo_role=x_demo_role)

List Cards

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
    api_instance = payfound_sdk.MerchantReportsApi(api_client)
    merchant_id = 'merchant_id_example' # str | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # List Cards
        api_response = api_instance.list_cards_api_merchant_report_cards_get(merchant_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantReportsApi->list_cards_api_merchant_report_cards_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantReportsApi->list_cards_api_merchant_report_cards_get: %s\n" % e)
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

# **open_card_api_merchant_report_cards_card_id_get**
> object open_card_api_merchant_report_cards_card_id_get(card_id, authorization=authorization, x_demo_role=x_demo_role)

Open Card

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
    api_instance = payfound_sdk.MerchantReportsApi(api_client)
    card_id = 'card_id_example' # str | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Open Card
        api_response = api_instance.open_card_api_merchant_report_cards_card_id_get(card_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantReportsApi->open_card_api_merchant_report_cards_card_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantReportsApi->open_card_api_merchant_report_cards_card_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **card_id** | **str**|  | 
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

# **preview_api_merchant_report_cards_preview_get**
> object preview_api_merchant_report_cards_preview_get(merchant_id, kind=kind, days=days, focus=focus, authorization=authorization, x_demo_role=x_demo_role)

Preview

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
    api_instance = payfound_sdk.MerchantReportsApi(api_client)
    merchant_id = 'merchant_id_example' # str | 
    kind = 'full' # str |  (optional) (default to 'full')
    days = 30 # int |  (optional) (default to 30)
    focus = 'focus_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Preview
        api_response = api_instance.preview_api_merchant_report_cards_preview_get(merchant_id, kind=kind, days=days, focus=focus, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantReportsApi->preview_api_merchant_report_cards_preview_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantReportsApi->preview_api_merchant_report_cards_preview_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **merchant_id** | **str**|  | 
 **kind** | **str**|  | [optional] [default to &#39;full&#39;]
 **days** | **int**|  | [optional] [default to 30]
 **focus** | **str**|  | [optional] 
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

# **report_pack_api_merchant_report_pack_get**
> object report_pack_api_merchant_report_pack_get(merchant_id, days=days, low_stock_threshold=low_stock_threshold, authorization=authorization, x_demo_role=x_demo_role)

Report Pack

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
    api_instance = payfound_sdk.MerchantReportsApi(api_client)
    merchant_id = 'merchant_id_example' # str | 
    days = 30 # int |  (optional) (default to 30)
    low_stock_threshold = 3 # int |  (optional) (default to 3)
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Report Pack
        api_response = api_instance.report_pack_api_merchant_report_pack_get(merchant_id, days=days, low_stock_threshold=low_stock_threshold, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantReportsApi->report_pack_api_merchant_report_pack_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantReportsApi->report_pack_api_merchant_report_pack_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **merchant_id** | **str**|  | 
 **days** | **int**|  | [optional] [default to 30]
 **low_stock_threshold** | **int**|  | [optional] [default to 3]
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

