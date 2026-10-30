# payfound_sdk.AccountHubApi

All URIs are relative to *http://127.0.0.1:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_ticket_api_me_support_tickets_post**](AccountHubApi.md#create_ticket_api_me_support_tickets_post) | **POST** /api/me/support-tickets | Create Ticket
[**get_thread_api_me_messages_thread_id_get**](AccountHubApi.md#get_thread_api_me_messages_thread_id_get) | **GET** /api/me/messages/{thread_id} | Get Thread
[**link_paypal_sandbox_api_me_payment_methods_paypal_sandbox_post**](AccountHubApi.md#link_paypal_sandbox_api_me_payment_methods_paypal_sandbox_post) | **POST** /api/me/payment-methods/paypal-sandbox | Link Paypal Sandbox
[**list_payment_methods_api_me_payment_methods_get**](AccountHubApi.md#list_payment_methods_api_me_payment_methods_get) | **GET** /api/me/payment-methods | List Payment Methods
[**list_threads_api_me_messages_get**](AccountHubApi.md#list_threads_api_me_messages_get) | **GET** /api/me/messages | List Threads
[**list_tickets_api_me_support_tickets_get**](AccountHubApi.md#list_tickets_api_me_support_tickets_get) | **GET** /api/me/support-tickets | List Tickets
[**post_message_api_me_messages_thread_id_post**](AccountHubApi.md#post_message_api_me_messages_thread_id_post) | **POST** /api/me/messages/{thread_id} | Post Message
[**start_thread_api_me_messages_start_post**](AccountHubApi.md#start_thread_api_me_messages_start_post) | **POST** /api/me/messages/start | Start Thread
[**unlink_payment_method_api_me_payment_methods_method_id_delete**](AccountHubApi.md#unlink_payment_method_api_me_payment_methods_method_id_delete) | **DELETE** /api/me/payment-methods/{method_id} | Unlink Payment Method


# **create_ticket_api_me_support_tickets_post**
> object create_ticket_api_me_support_tickets_post(ticket_input, authorization=authorization, x_demo_role=x_demo_role)

Create Ticket

### Example

* Api Key Authentication (demoRole):
* Bearer Authentication (bearerAuth):

```python
import payfound_sdk
from payfound_sdk.models.ticket_input import TicketInput
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
    api_instance = payfound_sdk.AccountHubApi(api_client)
    ticket_input = payfound_sdk.TicketInput() # TicketInput | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Create Ticket
        api_response = api_instance.create_ticket_api_me_support_tickets_post(ticket_input, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of AccountHubApi->create_ticket_api_me_support_tickets_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccountHubApi->create_ticket_api_me_support_tickets_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **ticket_input** | [**TicketInput**](TicketInput.md)|  | 
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

# **get_thread_api_me_messages_thread_id_get**
> object get_thread_api_me_messages_thread_id_get(thread_id, authorization=authorization, x_demo_role=x_demo_role)

Get Thread

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
    api_instance = payfound_sdk.AccountHubApi(api_client)
    thread_id = 'thread_id_example' # str | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Get Thread
        api_response = api_instance.get_thread_api_me_messages_thread_id_get(thread_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of AccountHubApi->get_thread_api_me_messages_thread_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccountHubApi->get_thread_api_me_messages_thread_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **thread_id** | **str**|  | 
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

# **link_paypal_sandbox_api_me_payment_methods_paypal_sandbox_post**
> object link_paypal_sandbox_api_me_payment_methods_paypal_sandbox_post(pay_pal_link_input, authorization=authorization, x_demo_role=x_demo_role)

Link Paypal Sandbox

### Example

* Api Key Authentication (demoRole):
* Bearer Authentication (bearerAuth):

```python
import payfound_sdk
from payfound_sdk.models.pay_pal_link_input import PayPalLinkInput
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
    api_instance = payfound_sdk.AccountHubApi(api_client)
    pay_pal_link_input = payfound_sdk.PayPalLinkInput() # PayPalLinkInput | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Link Paypal Sandbox
        api_response = api_instance.link_paypal_sandbox_api_me_payment_methods_paypal_sandbox_post(pay_pal_link_input, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of AccountHubApi->link_paypal_sandbox_api_me_payment_methods_paypal_sandbox_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccountHubApi->link_paypal_sandbox_api_me_payment_methods_paypal_sandbox_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **pay_pal_link_input** | [**PayPalLinkInput**](PayPalLinkInput.md)|  | 
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

# **list_payment_methods_api_me_payment_methods_get**
> object list_payment_methods_api_me_payment_methods_get(authorization=authorization, x_demo_role=x_demo_role)

List Payment Methods

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
    api_instance = payfound_sdk.AccountHubApi(api_client)
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # List Payment Methods
        api_response = api_instance.list_payment_methods_api_me_payment_methods_get(authorization=authorization, x_demo_role=x_demo_role)
        print("The response of AccountHubApi->list_payment_methods_api_me_payment_methods_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccountHubApi->list_payment_methods_api_me_payment_methods_get: %s\n" % e)
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

# **list_threads_api_me_messages_get**
> object list_threads_api_me_messages_get(authorization=authorization, x_demo_role=x_demo_role)

List Threads

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
    api_instance = payfound_sdk.AccountHubApi(api_client)
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # List Threads
        api_response = api_instance.list_threads_api_me_messages_get(authorization=authorization, x_demo_role=x_demo_role)
        print("The response of AccountHubApi->list_threads_api_me_messages_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccountHubApi->list_threads_api_me_messages_get: %s\n" % e)
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

# **list_tickets_api_me_support_tickets_get**
> object list_tickets_api_me_support_tickets_get(authorization=authorization, x_demo_role=x_demo_role)

List Tickets

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
    api_instance = payfound_sdk.AccountHubApi(api_client)
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # List Tickets
        api_response = api_instance.list_tickets_api_me_support_tickets_get(authorization=authorization, x_demo_role=x_demo_role)
        print("The response of AccountHubApi->list_tickets_api_me_support_tickets_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccountHubApi->list_tickets_api_me_support_tickets_get: %s\n" % e)
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

# **post_message_api_me_messages_thread_id_post**
> object post_message_api_me_messages_thread_id_post(thread_id, message_input, authorization=authorization, x_demo_role=x_demo_role)

Post Message

### Example

* Api Key Authentication (demoRole):
* Bearer Authentication (bearerAuth):

```python
import payfound_sdk
from payfound_sdk.models.message_input import MessageInput
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
    api_instance = payfound_sdk.AccountHubApi(api_client)
    thread_id = 'thread_id_example' # str | 
    message_input = payfound_sdk.MessageInput() # MessageInput | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Post Message
        api_response = api_instance.post_message_api_me_messages_thread_id_post(thread_id, message_input, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of AccountHubApi->post_message_api_me_messages_thread_id_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccountHubApi->post_message_api_me_messages_thread_id_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **thread_id** | **str**|  | 
 **message_input** | [**MessageInput**](MessageInput.md)|  | 
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

# **start_thread_api_me_messages_start_post**
> object start_thread_api_me_messages_start_post(start_input, authorization=authorization, x_demo_role=x_demo_role)

Start Thread

### Example

* Api Key Authentication (demoRole):
* Bearer Authentication (bearerAuth):

```python
import payfound_sdk
from payfound_sdk.models.start_input import StartInput
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
    api_instance = payfound_sdk.AccountHubApi(api_client)
    start_input = payfound_sdk.StartInput() # StartInput | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Start Thread
        api_response = api_instance.start_thread_api_me_messages_start_post(start_input, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of AccountHubApi->start_thread_api_me_messages_start_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccountHubApi->start_thread_api_me_messages_start_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **start_input** | [**StartInput**](StartInput.md)|  | 
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

# **unlink_payment_method_api_me_payment_methods_method_id_delete**
> object unlink_payment_method_api_me_payment_methods_method_id_delete(method_id, authorization=authorization, x_demo_role=x_demo_role)

Unlink Payment Method

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
    api_instance = payfound_sdk.AccountHubApi(api_client)
    method_id = 'method_id_example' # str | 
    authorization = 'authorization_example' # str |  (optional)
    x_demo_role = 'x_demo_role_example' # str |  (optional)

    try:
        # Unlink Payment Method
        api_response = api_instance.unlink_payment_method_api_me_payment_methods_method_id_delete(method_id, authorization=authorization, x_demo_role=x_demo_role)
        print("The response of AccountHubApi->unlink_payment_method_api_me_payment_methods_method_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AccountHubApi->unlink_payment_method_api_me_payment_methods_method_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **method_id** | **str**|  | 
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

