# PaypalAccountsApi

All URIs are relative to *http://127.0.0.1:8000*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**disconnectAccountApiMerchantsMerchantIdPaypalAccountDelete**](PaypalAccountsApi.md#disconnectaccountapimerchantsmerchantidpaypalaccountdelete) | **DELETE** /api/merchants/{merchant_id}/paypal-account | Disconnect Account |
| [**getAccountApiMerchantsMerchantIdPaypalAccountGet**](PaypalAccountsApi.md#getaccountapimerchantsmerchantidpaypalaccountget) | **GET** /api/merchants/{merchant_id}/paypal-account | Get Account |
| [**paymentHistoryApiMerchantsMerchantIdPaymentsGet**](PaypalAccountsApi.md#paymenthistoryapimerchantsmerchantidpaymentsget) | **GET** /api/merchants/{merchant_id}/payments | Payment History |
| [**saveAccountApiMerchantsMerchantIdPaypalAccountPut**](PaypalAccountsApi.md#saveaccountapimerchantsmerchantidpaypalaccountput) | **PUT** /api/merchants/{merchant_id}/paypal-account | Save Account |
| [**testAccountApiMerchantsMerchantIdPaypalAccountTestPost**](PaypalAccountsApi.md#testaccountapimerchantsmerchantidpaypalaccounttestpost) | **POST** /api/merchants/{merchant_id}/paypal-account/test | Test Account |



## disconnectAccountApiMerchantsMerchantIdPaypalAccountDelete

> any disconnectAccountApiMerchantsMerchantIdPaypalAccountDelete(merchantId, authorization, xDemoRole)

Disconnect Account

### Example

```ts
import {
  Configuration,
  PaypalAccountsApi,
} from 'payfound-sdk';
import type { DisconnectAccountApiMerchantsMerchantIdPaypalAccountDeleteRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new PaypalAccountsApi(config);

  const body = {
    // string
    merchantId: merchantId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies DisconnectAccountApiMerchantsMerchantIdPaypalAccountDeleteRequest;

  try {
    const data = await api.disconnectAccountApiMerchantsMerchantIdPaypalAccountDelete(body);
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
| **merchantId** | `string` |  | [Defaults to `undefined`] |
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


## getAccountApiMerchantsMerchantIdPaypalAccountGet

> any getAccountApiMerchantsMerchantIdPaypalAccountGet(merchantId, authorization, xDemoRole)

Get Account

### Example

```ts
import {
  Configuration,
  PaypalAccountsApi,
} from 'payfound-sdk';
import type { GetAccountApiMerchantsMerchantIdPaypalAccountGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new PaypalAccountsApi(config);

  const body = {
    // string
    merchantId: merchantId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies GetAccountApiMerchantsMerchantIdPaypalAccountGetRequest;

  try {
    const data = await api.getAccountApiMerchantsMerchantIdPaypalAccountGet(body);
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
| **merchantId** | `string` |  | [Defaults to `undefined`] |
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


## paymentHistoryApiMerchantsMerchantIdPaymentsGet

> any paymentHistoryApiMerchantsMerchantIdPaymentsGet(merchantId, stage, limit, offset, authorization, xDemoRole)

Payment History

### Example

```ts
import {
  Configuration,
  PaypalAccountsApi,
} from 'payfound-sdk';
import type { PaymentHistoryApiMerchantsMerchantIdPaymentsGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new PaypalAccountsApi(config);

  const body = {
    // string
    merchantId: merchantId_example,
    // string (optional)
    stage: stage_example,
    // number (optional)
    limit: 56,
    // number (optional)
    offset: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies PaymentHistoryApiMerchantsMerchantIdPaymentsGetRequest;

  try {
    const data = await api.paymentHistoryApiMerchantsMerchantIdPaymentsGet(body);
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
| **merchantId** | `string` |  | [Defaults to `undefined`] |
| **stage** | `string` |  | [Optional] [Defaults to `undefined`] |
| **limit** | `number` |  | [Optional] [Defaults to `100`] |
| **offset** | `number` |  | [Optional] [Defaults to `0`] |
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


## saveAccountApiMerchantsMerchantIdPaypalAccountPut

> any saveAccountApiMerchantsMerchantIdPaypalAccountPut(merchantId, accountInput, authorization, xDemoRole)

Save Account

### Example

```ts
import {
  Configuration,
  PaypalAccountsApi,
} from 'payfound-sdk';
import type { SaveAccountApiMerchantsMerchantIdPaypalAccountPutRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new PaypalAccountsApi(config);

  const body = {
    // string
    merchantId: merchantId_example,
    // AccountInput
    accountInput: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies SaveAccountApiMerchantsMerchantIdPaypalAccountPutRequest;

  try {
    const data = await api.saveAccountApiMerchantsMerchantIdPaypalAccountPut(body);
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
| **merchantId** | `string` |  | [Defaults to `undefined`] |
| **accountInput** | [AccountInput](AccountInput.md) |  | |
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
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## testAccountApiMerchantsMerchantIdPaypalAccountTestPost

> any testAccountApiMerchantsMerchantIdPaypalAccountTestPost(merchantId, authorization, xDemoRole)

Test Account

### Example

```ts
import {
  Configuration,
  PaypalAccountsApi,
} from 'payfound-sdk';
import type { TestAccountApiMerchantsMerchantIdPaypalAccountTestPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new PaypalAccountsApi(config);

  const body = {
    // string
    merchantId: merchantId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies TestAccountApiMerchantsMerchantIdPaypalAccountTestPostRequest;

  try {
    const data = await api.testAccountApiMerchantsMerchantIdPaypalAccountTestPost(body);
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
| **merchantId** | `string` |  | [Defaults to `undefined`] |
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

