# MerchantsApi

All URIs are relative to *http://127.0.0.1:8000*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**billingCancelApiMerchantsMerchantIdBillingCancelPost**](MerchantsApi.md#billingcancelapimerchantsmerchantidbillingcancelpost) | **POST** /api/merchants/{merchant_id}/billing/cancel | Billing Cancel |
| [**billingSubscriptionApiMerchantsMerchantIdBillingSubscriptionGet**](MerchantsApi.md#billingsubscriptionapimerchantsmerchantidbillingsubscriptionget) | **GET** /api/merchants/{merchant_id}/billing/subscription | Billing Subscription |
| [**changeSubscriptionApiMerchantsMerchantIdSubscriptionPost**](MerchantsApi.md#changesubscriptionapimerchantsmerchantidsubscriptionpost) | **POST** /api/merchants/{merchant_id}/subscription | Change Subscription |
| [**getSubscriptionApiMerchantsMerchantIdSubscriptionGet**](MerchantsApi.md#getsubscriptionapimerchantsmerchantidsubscriptionget) | **GET** /api/merchants/{merchant_id}/subscription | Get Subscription |
| [**listConversationsApiMerchantsMerchantIdMessagesGet**](MerchantsApi.md#listconversationsapimerchantsmerchantidmessagesget) | **GET** /api/merchants/{merchant_id}/messages | List Conversations |
| [**listReviewsApiMerchantsMerchantIdReviewsGet**](MerchantsApi.md#listreviewsapimerchantsmerchantidreviewsget) | **GET** /api/merchants/{merchant_id}/reviews | List Reviews |
| [**merchantDetailApiMerchantsSlugGet**](MerchantsApi.md#merchantdetailapimerchantsslugget) | **GET** /api/merchants/{slug} | Merchant Detail |
| [**merchantPaymentReconcileApiMerchantsMerchantIdPaymentsOrderIdReconcilePost**](MerchantsApi.md#merchantpaymentreconcileapimerchantsmerchantidpaymentsorderidreconcilepost) | **POST** /api/merchants/{merchant_id}/payments/{order_id}/reconcile | Merchant Payment Reconcile |
| [**merchantsApiMerchantsGet**](MerchantsApi.md#merchantsapimerchantsget) | **GET** /api/merchants | Merchants |
| [**pickupSlotsApiMerchantsMerchantIdPickupSlotsGet**](MerchantsApi.md#pickupslotsapimerchantsmerchantidpickupslotsget) | **GET** /api/merchants/{merchant_id}/pickup-slots | Pickup Slots |
| [**replyReviewApiMerchantsMerchantIdReviewsReviewIdReplyPost**](MerchantsApi.md#replyreviewapimerchantsmerchantidreviewsreviewidreplypost) | **POST** /api/merchants/{merchant_id}/reviews/{review_id}/reply | Reply Review |
| [**subscribeApiMerchantsMerchantIdBillingSubscribePost**](MerchantsApi.md#subscribeapimerchantsmerchantidbillingsubscribepost) | **POST** /api/merchants/{merchant_id}/billing/subscribe | Subscribe |



## billingCancelApiMerchantsMerchantIdBillingCancelPost

> any billingCancelApiMerchantsMerchantIdBillingCancelPost(merchantId, authorization, xDemoRole)

Billing Cancel

### Example

```ts
import {
  Configuration,
  MerchantsApi,
} from 'payfound-sdk';
import type { BillingCancelApiMerchantsMerchantIdBillingCancelPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantsApi(config);

  const body = {
    // string
    merchantId: merchantId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies BillingCancelApiMerchantsMerchantIdBillingCancelPostRequest;

  try {
    const data = await api.billingCancelApiMerchantsMerchantIdBillingCancelPost(body);
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


## billingSubscriptionApiMerchantsMerchantIdBillingSubscriptionGet

> any billingSubscriptionApiMerchantsMerchantIdBillingSubscriptionGet(merchantId, authorization, xDemoRole)

Billing Subscription

### Example

```ts
import {
  Configuration,
  MerchantsApi,
} from 'payfound-sdk';
import type { BillingSubscriptionApiMerchantsMerchantIdBillingSubscriptionGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantsApi(config);

  const body = {
    // string
    merchantId: merchantId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies BillingSubscriptionApiMerchantsMerchantIdBillingSubscriptionGetRequest;

  try {
    const data = await api.billingSubscriptionApiMerchantsMerchantIdBillingSubscriptionGet(body);
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


## changeSubscriptionApiMerchantsMerchantIdSubscriptionPost

> any changeSubscriptionApiMerchantsMerchantIdSubscriptionPost(merchantId, planChange, authorization, xDemoRole)

Change Subscription

### Example

```ts
import {
  Configuration,
  MerchantsApi,
} from 'payfound-sdk';
import type { ChangeSubscriptionApiMerchantsMerchantIdSubscriptionPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantsApi(config);

  const body = {
    // string
    merchantId: merchantId_example,
    // PlanChange
    planChange: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies ChangeSubscriptionApiMerchantsMerchantIdSubscriptionPostRequest;

  try {
    const data = await api.changeSubscriptionApiMerchantsMerchantIdSubscriptionPost(body);
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
| **planChange** | [PlanChange](PlanChange.md) |  | |
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


## getSubscriptionApiMerchantsMerchantIdSubscriptionGet

> any getSubscriptionApiMerchantsMerchantIdSubscriptionGet(merchantId, authorization, xDemoRole)

Get Subscription

### Example

```ts
import {
  Configuration,
  MerchantsApi,
} from 'payfound-sdk';
import type { GetSubscriptionApiMerchantsMerchantIdSubscriptionGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantsApi(config);

  const body = {
    // string
    merchantId: merchantId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies GetSubscriptionApiMerchantsMerchantIdSubscriptionGetRequest;

  try {
    const data = await api.getSubscriptionApiMerchantsMerchantIdSubscriptionGet(body);
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


## listConversationsApiMerchantsMerchantIdMessagesGet

> any listConversationsApiMerchantsMerchantIdMessagesGet(merchantId, authorization, xDemoRole)

List Conversations

### Example

```ts
import {
  Configuration,
  MerchantsApi,
} from 'payfound-sdk';
import type { ListConversationsApiMerchantsMerchantIdMessagesGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantsApi(config);

  const body = {
    // string
    merchantId: merchantId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies ListConversationsApiMerchantsMerchantIdMessagesGetRequest;

  try {
    const data = await api.listConversationsApiMerchantsMerchantIdMessagesGet(body);
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


## listReviewsApiMerchantsMerchantIdReviewsGet

> any listReviewsApiMerchantsMerchantIdReviewsGet(merchantId, authorization, xDemoRole)

List Reviews

### Example

```ts
import {
  Configuration,
  MerchantsApi,
} from 'payfound-sdk';
import type { ListReviewsApiMerchantsMerchantIdReviewsGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantsApi(config);

  const body = {
    // string
    merchantId: merchantId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies ListReviewsApiMerchantsMerchantIdReviewsGetRequest;

  try {
    const data = await api.listReviewsApiMerchantsMerchantIdReviewsGet(body);
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


## merchantDetailApiMerchantsSlugGet

> any merchantDetailApiMerchantsSlugGet(slug)

Merchant Detail

### Example

```ts
import {
  Configuration,
  MerchantsApi,
} from 'payfound-sdk';
import type { MerchantDetailApiMerchantsSlugGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantsApi(config);

  const body = {
    // string
    slug: slug_example,
  } satisfies MerchantDetailApiMerchantsSlugGetRequest;

  try {
    const data = await api.merchantDetailApiMerchantsSlugGet(body);
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
| **slug** | `string` |  | [Defaults to `undefined`] |

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


## merchantPaymentReconcileApiMerchantsMerchantIdPaymentsOrderIdReconcilePost

> any merchantPaymentReconcileApiMerchantsMerchantIdPaymentsOrderIdReconcilePost(merchantId, orderId, authorization, xDemoRole)

Merchant Payment Reconcile

### Example

```ts
import {
  Configuration,
  MerchantsApi,
} from 'payfound-sdk';
import type { MerchantPaymentReconcileApiMerchantsMerchantIdPaymentsOrderIdReconcilePostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantsApi(config);

  const body = {
    // string
    merchantId: merchantId_example,
    // string
    orderId: orderId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies MerchantPaymentReconcileApiMerchantsMerchantIdPaymentsOrderIdReconcilePostRequest;

  try {
    const data = await api.merchantPaymentReconcileApiMerchantsMerchantIdPaymentsOrderIdReconcilePost(body);
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
| **orderId** | `string` |  | [Defaults to `undefined`] |
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


## merchantsApiMerchantsGet

> any merchantsApiMerchantsGet(limit, offset)

Merchants

### Example

```ts
import {
  Configuration,
  MerchantsApi,
} from 'payfound-sdk';
import type { MerchantsApiMerchantsGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantsApi(config);

  const body = {
    // number (optional)
    limit: 56,
    // number (optional)
    offset: 56,
  } satisfies MerchantsApiMerchantsGetRequest;

  try {
    const data = await api.merchantsApiMerchantsGet(body);
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
| **limit** | `number` |  | [Optional] [Defaults to `200`] |
| **offset** | `number` |  | [Optional] [Defaults to `0`] |

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


## pickupSlotsApiMerchantsMerchantIdPickupSlotsGet

> any pickupSlotsApiMerchantsMerchantIdPickupSlotsGet(merchantId, date, locationId, viewTimezone)

Pickup Slots

### Example

```ts
import {
  Configuration,
  MerchantsApi,
} from 'payfound-sdk';
import type { PickupSlotsApiMerchantsMerchantIdPickupSlotsGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantsApi(config);

  const body = {
    // string
    merchantId: merchantId_example,
    // Date
    date: 2013-10-20,
    // string (optional)
    locationId: locationId_example,
    // string (optional)
    viewTimezone: viewTimezone_example,
  } satisfies PickupSlotsApiMerchantsMerchantIdPickupSlotsGetRequest;

  try {
    const data = await api.pickupSlotsApiMerchantsMerchantIdPickupSlotsGet(body);
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
| **date** | `Date` |  | [Defaults to `undefined`] |
| **locationId** | `string` |  | [Optional] [Defaults to `undefined`] |
| **viewTimezone** | `string` |  | [Optional] [Defaults to `undefined`] |

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


## replyReviewApiMerchantsMerchantIdReviewsReviewIdReplyPost

> any replyReviewApiMerchantsMerchantIdReviewsReviewIdReplyPost(merchantId, reviewId, replyInput, authorization, xDemoRole)

Reply Review

### Example

```ts
import {
  Configuration,
  MerchantsApi,
} from 'payfound-sdk';
import type { ReplyReviewApiMerchantsMerchantIdReviewsReviewIdReplyPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantsApi(config);

  const body = {
    // string
    merchantId: merchantId_example,
    // string
    reviewId: reviewId_example,
    // ReplyInput
    replyInput: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies ReplyReviewApiMerchantsMerchantIdReviewsReviewIdReplyPostRequest;

  try {
    const data = await api.replyReviewApiMerchantsMerchantIdReviewsReviewIdReplyPost(body);
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
| **reviewId** | `string` |  | [Defaults to `undefined`] |
| **replyInput** | [ReplyInput](ReplyInput.md) |  | |
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


## subscribeApiMerchantsMerchantIdBillingSubscribePost

> any subscribeApiMerchantsMerchantIdBillingSubscribePost(merchantId, subscribeBody, authorization, xDemoRole)

Subscribe

### Example

```ts
import {
  Configuration,
  MerchantsApi,
} from 'payfound-sdk';
import type { SubscribeApiMerchantsMerchantIdBillingSubscribePostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantsApi(config);

  const body = {
    // string
    merchantId: merchantId_example,
    // SubscribeBody
    subscribeBody: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies SubscribeApiMerchantsMerchantIdBillingSubscribePostRequest;

  try {
    const data = await api.subscribeApiMerchantsMerchantIdBillingSubscribePost(body);
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
| **subscribeBody** | [SubscribeBody](SubscribeBody.md) |  | |
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

