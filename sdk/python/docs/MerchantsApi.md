# payfound_sdk.MerchantsApi

All URIs are relative to *http://127.0.0.1:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**billing_cancel_api_merchants_merchant_id_billing_cancel_post**](MerchantsApi.md#billing_cancel_api_merchants_merchant_id_billing_cancel_post) | **POST** /api/merchants/{merchant_id}/billing/cancel | Billing Cancel
[**billing_subscription_api_merchants_merchant_id_billing_subscription_get**](MerchantsApi.md#billing_subscription_api_merchants_merchant_id_billing_subscription_get) | **GET** /api/merchants/{merchant_id}/billing/subscription | Billing Subscription
[**change_subscription_api_merchants_merchant_id_subscription_post**](MerchantsApi.md#change_subscription_api_merchants_merchant_id_subscription_post) | **POST** /api/merchants/{merchant_id}/subscription | Change Subscription
[**get_subscription_api_merchants_merchant_id_subscription_get**](MerchantsApi.md#get_subscription_api_merchants_merchant_id_subscription_get) | **GET** /api/merchants/{merchant_id}/subscription | Get Subscription
[**list_conversations_api_merchants_merchant_id_messages_get**](MerchantsApi.md#list_conversations_api_merchants_merchant_id_messages_get) | **GET** /api/merchants/{merchant_id}/messages | List Conversations
[**list_reviews_api_merchants_merchant_id_reviews_get**](MerchantsApi.md#list_reviews_api_merchants_merchant_id_reviews_get) | **GET** /api/merchants/{merchant_id}/reviews | List Reviews
[**merchant_detail_api_merchants_slug_get**](MerchantsApi.md#merchant_detail_api_merchants_slug_get) | **GET** /api/merchants/{slug} | Merchant Detail
[**merchant_payment_reconcile_api_merchants_merchant_id_payments_order_id_reconcile_post**](MerchantsApi.md#merchant_payment_reconcile_api_merchants_merchant_id_payments_order_id_reconcile_post) | **POST** /api/merchants/{merchant_id}/payments/{order_id}/reconcile | Merchant Payment Reconcile
[**merchants_api_merchants_get**](MerchantsApi.md#merchants_api_merchants_get) | **GET** /api/merchants | Merchants
[**pickup_slots_api_merchants_merchant_id_pickup_slots_get**](MerchantsApi.md#pickup_slots_api_merchants_merchant_id_pickup_slots_get) | **GET** /api/merchants/{merchant_id}/pickup-slots | Pickup Slots
[**reply_review_api_merchants_merchant_id_reviews_review_id_reply_post**](MerchantsApi.md#reply_review_api_merchants_merchant_id_reviews_review_id_reply_post) | **POST** /api/merchants/{merchant_id}/reviews/{review_id}/reply | Reply Review
[**subscribe_api_merchants_merchant_id_billing_subscribe_post**](MerchantsApi.md#subscribe_api_merchants_merchant_id_billing_subscribe_post) | **POST** /api/merchants/{merchant_id}/billing/subscribe | Subscribe


# **billing_cancel_api_merchants_merchant_id_billing_cancel_post**
> object billing_cancel_api_merchants_merchant_id_billing_cancel_post(merchant_id, authorization=authorization, x_demo_role=x_demo_role)

Billing Cancel

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
    api_instance = payfound_sdk.MerchantsApi(api_client)
    merchant_id = 'merchant_id_example' # str | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Billing Cancel
        api_response = api_instance.billing_cancel_api_merchants_merchant_id_billing_cancel_post(merchant_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantsApi->billing_cancel_api_merchants_merchant_id_billing_cancel_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantsApi->billing_cancel_api_merchants_merchant_id_billing_cancel_post: %s\n" % e)
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

# **billing_subscription_api_merchants_merchant_id_billing_subscription_get**
> object billing_subscription_api_merchants_merchant_id_billing_subscription_get(merchant_id, authorization=authorization, x_demo_role=x_demo_role)

Billing Subscription

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
    api_instance = payfound_sdk.MerchantsApi(api_client)
    merchant_id = 'merchant_id_example' # str | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Billing Subscription
        api_response = api_instance.billing_subscription_api_merchants_merchant_id_billing_subscription_get(merchant_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantsApi->billing_subscription_api_merchants_merchant_id_billing_subscription_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantsApi->billing_subscription_api_merchants_merchant_id_billing_subscription_get: %s\n" % e)
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

# **change_subscription_api_merchants_merchant_id_subscription_post**
> object change_subscription_api_merchants_merchant_id_subscription_post(merchant_id, plan_change, authorization=authorization, x_demo_role=x_demo_role)

Change Subscription

### Example

* Api Key Authentication (demoRole):
* Bearer Authentication (bearerAuth):

```python
import payfound_sdk
from payfound_sdk.models.plan_change import PlanChange
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
    api_instance = payfound_sdk.MerchantsApi(api_client)
    merchant_id = 'merchant_id_example' # str | 
    plan_change = payfound_sdk.PlanChange() # PlanChange | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Change Subscription
        api_response = api_instance.change_subscription_api_merchants_merchant_id_subscription_post(merchant_id, plan_change, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantsApi->change_subscription_api_merchants_merchant_id_subscription_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantsApi->change_subscription_api_merchants_merchant_id_subscription_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **merchant_id** | **str**|  | 
 **plan_change** | [**PlanChange**](PlanChange.md)|  | 
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

# **get_subscription_api_merchants_merchant_id_subscription_get**
> object get_subscription_api_merchants_merchant_id_subscription_get(merchant_id, authorization=authorization, x_demo_role=x_demo_role)

Get Subscription

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
    api_instance = payfound_sdk.MerchantsApi(api_client)
    merchant_id = 'merchant_id_example' # str | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Get Subscription
        api_response = api_instance.get_subscription_api_merchants_merchant_id_subscription_get(merchant_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantsApi->get_subscription_api_merchants_merchant_id_subscription_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantsApi->get_subscription_api_merchants_merchant_id_subscription_get: %s\n" % e)
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

# **list_conversations_api_merchants_merchant_id_messages_get**
> object list_conversations_api_merchants_merchant_id_messages_get(merchant_id, authorization=authorization, x_demo_role=x_demo_role)

List Conversations

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
    api_instance = payfound_sdk.MerchantsApi(api_client)
    merchant_id = 'merchant_id_example' # str | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # List Conversations
        api_response = api_instance.list_conversations_api_merchants_merchant_id_messages_get(merchant_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantsApi->list_conversations_api_merchants_merchant_id_messages_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantsApi->list_conversations_api_merchants_merchant_id_messages_get: %s\n" % e)
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

# **list_reviews_api_merchants_merchant_id_reviews_get**
> object list_reviews_api_merchants_merchant_id_reviews_get(merchant_id, authorization=authorization, x_demo_role=x_demo_role)

List Reviews

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
    api_instance = payfound_sdk.MerchantsApi(api_client)
    merchant_id = 'merchant_id_example' # str | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # List Reviews
        api_response = api_instance.list_reviews_api_merchants_merchant_id_reviews_get(merchant_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantsApi->list_reviews_api_merchants_merchant_id_reviews_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantsApi->list_reviews_api_merchants_merchant_id_reviews_get: %s\n" % e)
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

# **merchant_detail_api_merchants_slug_get**
> object merchant_detail_api_merchants_slug_get(slug)

Merchant Detail

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
    api_instance = payfound_sdk.MerchantsApi(api_client)
    slug = 'slug_example' # str | 

    try:
        # Merchant Detail
        api_response = api_instance.merchant_detail_api_merchants_slug_get(slug)
        print("The response of MerchantsApi->merchant_detail_api_merchants_slug_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantsApi->merchant_detail_api_merchants_slug_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **slug** | **str**|  | 

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

# **merchant_payment_reconcile_api_merchants_merchant_id_payments_order_id_reconcile_post**
> object merchant_payment_reconcile_api_merchants_merchant_id_payments_order_id_reconcile_post(merchant_id, order_id, authorization=authorization, x_demo_role=x_demo_role)

Merchant Payment Reconcile

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
    api_instance = payfound_sdk.MerchantsApi(api_client)
    merchant_id = 'merchant_id_example' # str | 
    order_id = 'order_id_example' # str | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Merchant Payment Reconcile
        api_response = api_instance.merchant_payment_reconcile_api_merchants_merchant_id_payments_order_id_reconcile_post(merchant_id, order_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantsApi->merchant_payment_reconcile_api_merchants_merchant_id_payments_order_id_reconcile_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantsApi->merchant_payment_reconcile_api_merchants_merchant_id_payments_order_id_reconcile_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **merchant_id** | **str**|  | 
 **order_id** | **str**|  | 
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

# **merchants_api_merchants_get**
> object merchants_api_merchants_get(limit=limit, offset=offset)

Merchants

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
    api_instance = payfound_sdk.MerchantsApi(api_client)
    limit = 200 # int |  (optional) (default to 200)
    offset = 0 # int |  (optional) (default to 0)

    try:
        # Merchants
        api_response = api_instance.merchants_api_merchants_get(limit=limit, offset=offset)
        print("The response of MerchantsApi->merchants_api_merchants_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantsApi->merchants_api_merchants_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**|  | [optional] [default to 200]
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

# **pickup_slots_api_merchants_merchant_id_pickup_slots_get**
> object pickup_slots_api_merchants_merchant_id_pickup_slots_get(merchant_id, var_date, location_id=location_id, view_timezone=view_timezone)

Pickup Slots

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
    api_instance = payfound_sdk.MerchantsApi(api_client)
    merchant_id = 'merchant_id_example' # str | 
    var_date = '2013-10-20' # date | 
    location_id = 'location_id_example' # str |  (optional)
    view_timezone = 'view_timezone_example' # str |  (optional)

    try:
        # Pickup Slots
        api_response = api_instance.pickup_slots_api_merchants_merchant_id_pickup_slots_get(merchant_id, var_date, location_id=location_id, view_timezone=view_timezone)
        print("The response of MerchantsApi->pickup_slots_api_merchants_merchant_id_pickup_slots_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantsApi->pickup_slots_api_merchants_merchant_id_pickup_slots_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **merchant_id** | **str**|  | 
 **var_date** | **date**|  | 
 **location_id** | **str**|  | [optional] 
 **view_timezone** | **str**|  | [optional] 

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

# **reply_review_api_merchants_merchant_id_reviews_review_id_reply_post**
> object reply_review_api_merchants_merchant_id_reviews_review_id_reply_post(merchant_id, review_id, reply_input, authorization=authorization, x_demo_role=x_demo_role)

Reply Review

### Example

* Api Key Authentication (demoRole):
* Bearer Authentication (bearerAuth):

```python
import payfound_sdk
from payfound_sdk.models.reply_input import ReplyInput
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
    api_instance = payfound_sdk.MerchantsApi(api_client)
    merchant_id = 'merchant_id_example' # str | 
    review_id = 'review_id_example' # str | 
    reply_input = payfound_sdk.ReplyInput() # ReplyInput | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Reply Review
        api_response = api_instance.reply_review_api_merchants_merchant_id_reviews_review_id_reply_post(merchant_id, review_id, reply_input, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantsApi->reply_review_api_merchants_merchant_id_reviews_review_id_reply_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantsApi->reply_review_api_merchants_merchant_id_reviews_review_id_reply_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **merchant_id** | **str**|  | 
 **review_id** | **str**|  | 
 **reply_input** | [**ReplyInput**](ReplyInput.md)|  | 
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

# **subscribe_api_merchants_merchant_id_billing_subscribe_post**
> object subscribe_api_merchants_merchant_id_billing_subscribe_post(merchant_id, subscribe_body, authorization=authorization, x_demo_role=x_demo_role)

Subscribe

### Example

* Api Key Authentication (demoRole):
* Bearer Authentication (bearerAuth):

```python
import payfound_sdk
from payfound_sdk.models.subscribe_body import SubscribeBody
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
    api_instance = payfound_sdk.MerchantsApi(api_client)
    merchant_id = 'merchant_id_example' # str | 
    subscribe_body = payfound_sdk.SubscribeBody() # SubscribeBody | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Subscribe
        api_response = api_instance.subscribe_api_merchants_merchant_id_billing_subscribe_post(merchant_id, subscribe_body, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of MerchantsApi->subscribe_api_merchants_merchant_id_billing_subscribe_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling MerchantsApi->subscribe_api_merchants_merchant_id_billing_subscribe_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **merchant_id** | **str**|  | 
 **subscribe_body** | [**SubscribeBody**](SubscribeBody.md)|  | 
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

