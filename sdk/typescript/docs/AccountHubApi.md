# AccountHubApi

All URIs are relative to *http://127.0.0.1:8000*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**createTicketApiMeSupportTicketsPost**](AccountHubApi.md#createticketapimesupportticketspost) | **POST** /api/me/support-tickets | Create Ticket |
| [**getThreadApiMeMessagesThreadIdGet**](AccountHubApi.md#getthreadapimemessagesthreadidget) | **GET** /api/me/messages/{thread_id} | Get Thread |
| [**linkPaypalSandboxApiMePaymentMethodsPaypalSandboxPost**](AccountHubApi.md#linkpaypalsandboxapimepaymentmethodspaypalsandboxpost) | **POST** /api/me/payment-methods/paypal-sandbox | Link Paypal Sandbox |
| [**listPaymentMethodsApiMePaymentMethodsGet**](AccountHubApi.md#listpaymentmethodsapimepaymentmethodsget) | **GET** /api/me/payment-methods | List Payment Methods |
| [**listThreadsApiMeMessagesGet**](AccountHubApi.md#listthreadsapimemessagesget) | **GET** /api/me/messages | List Threads |
| [**listTicketsApiMeSupportTicketsGet**](AccountHubApi.md#listticketsapimesupportticketsget) | **GET** /api/me/support-tickets | List Tickets |
| [**postMessageApiMeMessagesThreadIdPost**](AccountHubApi.md#postmessageapimemessagesthreadidpost) | **POST** /api/me/messages/{thread_id} | Post Message |
| [**startThreadApiMeMessagesStartPost**](AccountHubApi.md#startthreadapimemessagesstartpost) | **POST** /api/me/messages/start | Start Thread |
| [**unlinkPaymentMethodApiMePaymentMethodsMethodIdDelete**](AccountHubApi.md#unlinkpaymentmethodapimepaymentmethodsmethodiddelete) | **DELETE** /api/me/payment-methods/{method_id} | Unlink Payment Method |



## createTicketApiMeSupportTicketsPost

> any createTicketApiMeSupportTicketsPost(ticketInput, authorization, xDemoRole)

Create Ticket

### Example

```ts
import {
  Configuration,
  AccountHubApi,
} from 'payfound-sdk';
import type { CreateTicketApiMeSupportTicketsPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AccountHubApi(config);

  const body = {
    // TicketInput
    ticketInput: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies CreateTicketApiMeSupportTicketsPostRequest;

  try {
    const data = await api.createTicketApiMeSupportTicketsPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **ticketInput** | [TicketInput](TicketInput.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xDemoRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**any**

### Authorization

[demoRole](../README.md#demoRole), [bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## getThreadApiMeMessagesThreadIdGet

> any getThreadApiMeMessagesThreadIdGet(threadId, authorization, xDemoRole)

Get Thread

### Example

```ts
import {
  Configuration,
  AccountHubApi,
} from 'payfound-sdk';
import type { GetThreadApiMeMessagesThreadIdGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AccountHubApi(config);

  const body = {
    // string
    threadId: threadId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies GetThreadApiMeMessagesThreadIdGetRequest;

  try {
    const data = await api.getThreadApiMeMessagesThreadIdGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **threadId** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xDemoRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**any**

### Authorization

[demoRole](../README.md#demoRole), [bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## linkPaypalSandboxApiMePaymentMethodsPaypalSandboxPost

> any linkPaypalSandboxApiMePaymentMethodsPaypalSandboxPost(payPalLinkInput, authorization, xDemoRole)

Link Paypal Sandbox

### Example

```ts
import {
  Configuration,
  AccountHubApi,
} from 'payfound-sdk';
import type { LinkPaypalSandboxApiMePaymentMethodsPaypalSandboxPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AccountHubApi(config);

  const body = {
    // PayPalLinkInput
    payPalLinkInput: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies LinkPaypalSandboxApiMePaymentMethodsPaypalSandboxPostRequest;

  try {
    const data = await api.linkPaypalSandboxApiMePaymentMethodsPaypalSandboxPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **payPalLinkInput** | [PayPalLinkInput](PayPalLinkInput.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xDemoRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**any**

### Authorization

[demoRole](../README.md#demoRole), [bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## listPaymentMethodsApiMePaymentMethodsGet

> any listPaymentMethodsApiMePaymentMethodsGet(authorization, xDemoRole)

List Payment Methods

### Example

```ts
import {
  Configuration,
  AccountHubApi,
} from 'payfound-sdk';
import type { ListPaymentMethodsApiMePaymentMethodsGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AccountHubApi(config);

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies ListPaymentMethodsApiMePaymentMethodsGetRequest;

  try {
    const data = await api.listPaymentMethodsApiMePaymentMethodsGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xDemoRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**any**

### Authorization

[demoRole](../README.md#demoRole), [bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## listThreadsApiMeMessagesGet

> any listThreadsApiMeMessagesGet(authorization, xDemoRole)

List Threads

### Example

```ts
import {
  Configuration,
  AccountHubApi,
} from 'payfound-sdk';
import type { ListThreadsApiMeMessagesGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AccountHubApi(config);

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies ListThreadsApiMeMessagesGetRequest;

  try {
    const data = await api.listThreadsApiMeMessagesGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xDemoRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**any**

### Authorization

[demoRole](../README.md#demoRole), [bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## listTicketsApiMeSupportTicketsGet

> any listTicketsApiMeSupportTicketsGet(authorization, xDemoRole)

List Tickets

### Example

```ts
import {
  Configuration,
  AccountHubApi,
} from 'payfound-sdk';
import type { ListTicketsApiMeSupportTicketsGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AccountHubApi(config);

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies ListTicketsApiMeSupportTicketsGetRequest;

  try {
    const data = await api.listTicketsApiMeSupportTicketsGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xDemoRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**any**

### Authorization

[demoRole](../README.md#demoRole), [bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## postMessageApiMeMessagesThreadIdPost

> any postMessageApiMeMessagesThreadIdPost(threadId, messageInput, authorization, xDemoRole)

Post Message

### Example

```ts
import {
  Configuration,
  AccountHubApi,
} from 'payfound-sdk';
import type { PostMessageApiMeMessagesThreadIdPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AccountHubApi(config);

  const body = {
    // string
    threadId: threadId_example,
    // MessageInput
    messageInput: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies PostMessageApiMeMessagesThreadIdPostRequest;

  try {
    const data = await api.postMessageApiMeMessagesThreadIdPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **threadId** | `string` |  | [Defaults to `undefined`] |
| **messageInput** | [MessageInput](MessageInput.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xDemoRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**any**

### Authorization

[demoRole](../README.md#demoRole), [bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## startThreadApiMeMessagesStartPost

> any startThreadApiMeMessagesStartPost(startInput, authorization, xDemoRole)

Start Thread

### Example

```ts
import {
  Configuration,
  AccountHubApi,
} from 'payfound-sdk';
import type { StartThreadApiMeMessagesStartPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AccountHubApi(config);

  const body = {
    // StartInput
    startInput: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies StartThreadApiMeMessagesStartPostRequest;

  try {
    const data = await api.startThreadApiMeMessagesStartPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **startInput** | [StartInput](StartInput.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xDemoRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**any**

### Authorization

[demoRole](../README.md#demoRole), [bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## unlinkPaymentMethodApiMePaymentMethodsMethodIdDelete

> any unlinkPaymentMethodApiMePaymentMethodsMethodIdDelete(methodId, authorization, xDemoRole)

Unlink Payment Method

### Example

```ts
import {
  Configuration,
  AccountHubApi,
} from 'payfound-sdk';
import type { UnlinkPaymentMethodApiMePaymentMethodsMethodIdDeleteRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AccountHubApi(config);

  const body = {
    // string
    methodId: methodId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies UnlinkPaymentMethodApiMePaymentMethodsMethodIdDeleteRequest;

  try {
    const data = await api.unlinkPaymentMethodApiMePaymentMethodsMethodIdDelete(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **methodId** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xDemoRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**any**

### Authorization

[demoRole](../README.md#demoRole), [bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

