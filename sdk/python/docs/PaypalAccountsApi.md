# payfound_sdk.PaypalAccountsApi

All URIs are relative to *http://127.0.0.1:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**disconnect_account_api_merchants_merchant_id_paypal_account_delete**](PaypalAccountsApi.md#disconnect_account_api_merchants_merchant_id_paypal_account_delete) | **DELETE** /api/merchants/{merchant_id}/paypal-account | Disconnect Account
[**get_account_api_merchants_merchant_id_paypal_account_get**](PaypalAccountsApi.md#get_account_api_merchants_merchant_id_paypal_account_get) | **GET** /api/merchants/{merchant_id}/paypal-account | Get Account
[**payment_history_api_merchants_merchant_id_payments_get**](PaypalAccountsApi.md#payment_history_api_merchants_merchant_id_payments_get) | **GET** /api/merchants/{merchant_id}/payments | Payment History
[**save_account_api_merchants_merchant_id_paypal_account_put**](PaypalAccountsApi.md#save_account_api_merchants_merchant_id_paypal_account_put) | **PUT** /api/merchants/{merchant_id}/paypal-account | Save Account
[**test_account_api_merchants_merchant_id_paypal_account_test_post**](PaypalAccountsApi.md#test_account_api_merchants_merchant_id_paypal_account_test_post) | **POST** /api/merchants/{merchant_id}/paypal-account/test | Test Account


# **disconnect_account_api_merchants_merchant_id_paypal_account_delete**
> object disconnect_account_api_merchants_merchant_id_paypal_account_delete(merchant_id, authorization=authorization, x_demo_role=x_demo_role)

Disconnect Account

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
    api_instance = payfound_sdk.PaypalAccountsApi(api_client)
    merchant_id = 'merchant_id_example' # str | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Disconnect Account
        api_response = api_instance.disconnect_account_api_merchants_merchant_id_paypal_account_delete(merchant_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of PaypalAccountsApi->disconnect_account_api_merchants_merchant_id_paypal_account_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PaypalAccountsApi->disconnect_account_api_merchants_merchant_id_paypal_account_delete: %s\n" % e)
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

# **get_account_api_merchants_merchant_id_paypal_account_get**
> object get_account_api_merchants_merchant_id_paypal_account_get(merchant_id, authorization=authorization, x_demo_role=x_demo_role)

Get Account

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
    api_instance = payfound_sdk.PaypalAccountsApi(api_client)
    merchant_id = 'merchant_id_example' # str | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Get Account
        api_response = api_instance.get_account_api_merchants_merchant_id_paypal_account_get(merchant_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of PaypalAccountsApi->get_account_api_merchants_merchant_id_paypal_account_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PaypalAccountsApi->get_account_api_merchants_merchant_id_paypal_account_get: %s\n" % e)
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

# **payment_history_api_merchants_merchant_id_payments_get**
> object payment_history_api_merchants_merchant_id_payments_get(merchant_id, stage=stage, limit=limit, offset=offset, authorization=authorization, x_demo_role=x_demo_role)

Payment History

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
    api_instance = payfound_sdk.PaypalAccountsApi(api_client)
    merchant_id = 'merchant_id_example' # str | 
    stage = 'stage_example' # str |  (optional)
    limit = 100 # int |  (optional) (default to 100)
    offset = 0 # int |  (optional) (default to 0)
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Payment History
        api_response = api_instance.payment_history_api_merchants_merchant_id_payments_get(merchant_id, stage=stage, limit=limit, offset=offset, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of PaypalAccountsApi->payment_history_api_merchants_merchant_id_payments_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PaypalAccountsApi->payment_history_api_merchants_merchant_id_payments_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **merchant_id** | **str**|  | 
 **stage** | **str**|  | [optional] 
 **limit** | **int**|  | [optional] [default to 100]
 **offset** | **int**|  | [optional] [default to 0]
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

# **save_account_api_merchants_merchant_id_paypal_account_put**
> object save_account_api_merchants_merchant_id_paypal_account_put(merchant_id, account_input, authorization=authorization, x_demo_role=x_demo_role)

Save Account

### Example

* Api Key Authentication (demoRole):
* Bearer Authentication (bearerAuth):

```python
import payfound_sdk
from payfound_sdk.models.account_input import AccountInput
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
    api_instance = payfound_sdk.PaypalAccountsApi(api_client)
    merchant_id = 'merchant_id_example' # str | 
    account_input = payfound_sdk.AccountInput() # AccountInput | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Save Account
        api_response = api_instance.save_account_api_merchants_merchant_id_paypal_account_put(merchant_id, account_input, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of PaypalAccountsApi->save_account_api_merchants_merchant_id_paypal_account_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PaypalAccountsApi->save_account_api_merchants_merchant_id_paypal_account_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **merchant_id** | **str**|  | 
 **account_input** | [**AccountInput**](AccountInput.md)|  | 
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

# **test_account_api_merchants_merchant_id_paypal_account_test_post**
> object test_account_api_merchants_merchant_id_paypal_account_test_post(merchant_id, authorization=authorization, x_demo_role=x_demo_role)

Test Account

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
    api_instance = payfound_sdk.PaypalAccountsApi(api_client)
    merchant_id = 'merchant_id_example' # str | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Test Account
        api_response = api_instance.test_account_api_merchants_merchant_id_paypal_account_test_post(merchant_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of PaypalAccountsApi->test_account_api_merchants_merchant_id_paypal_account_test_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PaypalAccountsApi->test_account_api_merchants_merchant_id_paypal_account_test_post: %s\n" % e)
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

