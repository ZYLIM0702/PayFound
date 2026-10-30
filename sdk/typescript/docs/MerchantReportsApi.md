# MerchantReportsApi

All URIs are relative to *http://127.0.0.1:8000*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**createCardApiMerchantReportCardsPost**](MerchantReportsApi.md#createcardapimerchantreportcardspost) | **POST** /api/merchant/report-cards | Create Card |
| [**deleteCardApiMerchantReportCardsCardIdDelete**](MerchantReportsApi.md#deletecardapimerchantreportcardscardiddelete) | **DELETE** /api/merchant/report-cards/{card_id} | Delete Card |
| [**listCardsApiMerchantReportCardsGet**](MerchantReportsApi.md#listcardsapimerchantreportcardsget) | **GET** /api/merchant/report-cards | List Cards |
| [**openCardApiMerchantReportCardsCardIdGet**](MerchantReportsApi.md#opencardapimerchantreportcardscardidget) | **GET** /api/merchant/report-cards/{card_id} | Open Card |
| [**previewApiMerchantReportCardsPreviewGet**](MerchantReportsApi.md#previewapimerchantreportcardspreviewget) | **GET** /api/merchant/report-cards/preview | Preview |
| [**reportPackApiMerchantReportPackGet**](MerchantReportsApi.md#reportpackapimerchantreportpackget) | **GET** /api/merchant/report-pack | Report Pack |



## createCardApiMerchantReportCardsPost

> any createCardApiMerchantReportCardsPost(cardSave, authorization, xDemoRole)

Create Card

### Example

```ts
import {
  Configuration,
  MerchantReportsApi,
} from 'payfound-sdk';
import type { CreateCardApiMerchantReportCardsPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantReportsApi(config);

  const body = {
    // CardSave
    cardSave: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies CreateCardApiMerchantReportCardsPostRequest;

  try {
    const data = await api.createCardApiMerchantReportCardsPost(body);
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
| **cardSave** | [CardSave](CardSave.md) |  | |
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


## deleteCardApiMerchantReportCardsCardIdDelete

> deleteCardApiMerchantReportCardsCardIdDelete(cardId, authorization, xDemoRole)

Delete Card

### Example

```ts
import {
  Configuration,
  MerchantReportsApi,
} from 'payfound-sdk';
import type { DeleteCardApiMerchantReportCardsCardIdDeleteRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantReportsApi(config);

  const body = {
    // string
    cardId: cardId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies DeleteCardApiMerchantReportCardsCardIdDeleteRequest;

  try {
    const data = await api.deleteCardApiMerchantReportCardsCardIdDelete(body);
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
| **cardId** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xDemoRole** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

`void` (Empty response body)

### Authorization

[demoRole](../README.md#demoRole), [bearerAuth](../README.md#bearerAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **204** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## listCardsApiMerchantReportCardsGet

> any listCardsApiMerchantReportCardsGet(merchantId, authorization, xDemoRole)

List Cards

### Example

```ts
import {
  Configuration,
  MerchantReportsApi,
} from 'payfound-sdk';
import type { ListCardsApiMerchantReportCardsGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantReportsApi(config);

  const body = {
    // string
    merchantId: merchantId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies ListCardsApiMerchantReportCardsGetRequest;

  try {
    const data = await api.listCardsApiMerchantReportCardsGet(body);
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


## openCardApiMerchantReportCardsCardIdGet

> any openCardApiMerchantReportCardsCardIdGet(cardId, authorization, xDemoRole)

Open Card

### Example

```ts
import {
  Configuration,
  MerchantReportsApi,
} from 'payfound-sdk';
import type { OpenCardApiMerchantReportCardsCardIdGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantReportsApi(config);

  const body = {
    // string
    cardId: cardId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies OpenCardApiMerchantReportCardsCardIdGetRequest;

  try {
    const data = await api.openCardApiMerchantReportCardsCardIdGet(body);
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
| **cardId** | `string` |  | [Defaults to `undefined`] |
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


## previewApiMerchantReportCardsPreviewGet

> any previewApiMerchantReportCardsPreviewGet(merchantId, kind, days, focus, authorization, xDemoRole)

Preview

### Example

```ts
import {
  Configuration,
  MerchantReportsApi,
} from 'payfound-sdk';
import type { PreviewApiMerchantReportCardsPreviewGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantReportsApi(config);

  const body = {
    // string
    merchantId: merchantId_example,
    // 'full' | 'sales' | 'products' | 'orders' | 'stock' | 'pickup' (optional)
    kind: kind_example,
    // number (optional)
    days: 56,
    // string (optional)
    focus: focus_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies PreviewApiMerchantReportCardsPreviewGetRequest;

  try {
    const data = await api.previewApiMerchantReportCardsPreviewGet(body);
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
| **kind** | `full`, `sales`, `products`, `orders`, `stock`, `pickup` |  | [Optional] [Defaults to `&#39;full&#39;`] [Enum: full, sales, products, orders, stock, pickup] |
| **days** | `number` |  | [Optional] [Defaults to `30`] |
| **focus** | `string` |  | [Optional] [Defaults to `undefined`] |
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


## reportPackApiMerchantReportPackGet

> any reportPackApiMerchantReportPackGet(merchantId, days, lowStockThreshold, authorization, xDemoRole)

Report Pack

### Example

```ts
import {
  Configuration,
  MerchantReportsApi,
} from 'payfound-sdk';
import type { ReportPackApiMerchantReportPackGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantReportsApi(config);

  const body = {
    // string
    merchantId: merchantId_example,
    // number (optional)
    days: 56,
    // number (optional)
    lowStockThreshold: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies ReportPackApiMerchantReportPackGetRequest;

  try {
    const data = await api.reportPackApiMerchantReportPackGet(body);
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
| **days** | `number` |  | [Optional] [Defaults to `30`] |
| **lowStockThreshold** | `number` |  | [Optional] [Defaults to `3`] |
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

