# SuggestionsAndPriceWatchesApi

All URIs are relative to *http://127.0.0.1:8000*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**competitorPricesApiMerchantsMerchantIdCompetitorPricesGet**](SuggestionsAndPriceWatchesApi.md#competitorpricesapimerchantsmerchantidcompetitorpricesget) | **GET** /api/merchants/{merchant_id}/competitor-prices | Competitor Prices |
| [**createPriceWatchApiMePriceWatchesPost**](SuggestionsAndPriceWatchesApi.md#createpricewatchapimepricewatchespost) | **POST** /api/me/price-watches | Create Price Watch |
| [**deletePriceWatchApiMePriceWatchesWatchIdDelete**](SuggestionsAndPriceWatchesApi.md#deletepricewatchapimepricewatcheswatchiddelete) | **DELETE** /api/me/price-watches/{watch_id} | Delete Price Watch |
| [**listPriceWatchesApiMePriceWatchesGet**](SuggestionsAndPriceWatchesApi.md#listpricewatchesapimepricewatchesget) | **GET** /api/me/price-watches | List Price Watches |
| [**pickupSuggestionsApiPickupSuggestionsGet**](SuggestionsAndPriceWatchesApi.md#pickupsuggestionsapipickupsuggestionsget) | **GET** /api/pickup-suggestions | Pickup Suggestions |
| [**stockUpApiMerchantsMerchantIdStockUpPost**](SuggestionsAndPriceWatchesApi.md#stockupapimerchantsmerchantidstockuppost) | **POST** /api/merchants/{merchant_id}/stock-up | Stock Up |



## competitorPricesApiMerchantsMerchantIdCompetitorPricesGet

> any competitorPricesApiMerchantsMerchantIdCompetitorPricesGet(merchantId, authorization, xDemoRole)

Competitor Prices

### Example

```ts
import {
  Configuration,
  SuggestionsAndPriceWatchesApi,
} from 'payfound-sdk';
import type { CompetitorPricesApiMerchantsMerchantIdCompetitorPricesGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new SuggestionsAndPriceWatchesApi(config);

  const body = {
    // string
    merchantId: merchantId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies CompetitorPricesApiMerchantsMerchantIdCompetitorPricesGetRequest;

  try {
    const data = await api.competitorPricesApiMerchantsMerchantIdCompetitorPricesGet(body);
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


## createPriceWatchApiMePriceWatchesPost

> any createPriceWatchApiMePriceWatchesPost(watchInput, authorization, xDemoRole)

Create Price Watch

### Example

```ts
import {
  Configuration,
  SuggestionsAndPriceWatchesApi,
} from 'payfound-sdk';
import type { CreatePriceWatchApiMePriceWatchesPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new SuggestionsAndPriceWatchesApi(config);

  const body = {
    // WatchInput
    watchInput: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies CreatePriceWatchApiMePriceWatchesPostRequest;

  try {
    const data = await api.createPriceWatchApiMePriceWatchesPost(body);
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
| **watchInput** | [WatchInput](WatchInput.md) |  | |
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


## deletePriceWatchApiMePriceWatchesWatchIdDelete

> deletePriceWatchApiMePriceWatchesWatchIdDelete(watchId, authorization, xDemoRole)

Delete Price Watch

### Example

```ts
import {
  Configuration,
  SuggestionsAndPriceWatchesApi,
} from 'payfound-sdk';
import type { DeletePriceWatchApiMePriceWatchesWatchIdDeleteRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new SuggestionsAndPriceWatchesApi(config);

  const body = {
    // string
    watchId: watchId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies DeletePriceWatchApiMePriceWatchesWatchIdDeleteRequest;

  try {
    const data = await api.deletePriceWatchApiMePriceWatchesWatchIdDelete(body);
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
| **watchId** | `string` |  | [Defaults to `undefined`] |
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


## listPriceWatchesApiMePriceWatchesGet

> any listPriceWatchesApiMePriceWatchesGet(authorization, xDemoRole)

List Price Watches

### Example

```ts
import {
  Configuration,
  SuggestionsAndPriceWatchesApi,
} from 'payfound-sdk';
import type { ListPriceWatchesApiMePriceWatchesGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new SuggestionsAndPriceWatchesApi(config);

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies ListPriceWatchesApiMePriceWatchesGetRequest;

  try {
    const data = await api.listPriceWatchesApiMePriceWatchesGet(body);
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


## pickupSuggestionsApiPickupSuggestionsGet

> any pickupSuggestionsApiPickupSuggestionsGet(merchantId, day, authorization, xDemoRole)

Pickup Suggestions

Top 5 pickup slots with room left on &#x60;day&#x60; (the store\&#39;s local day, per branch timezone).  queue_estimate_minutes &#x3D; round(booked / max(capacity, 1) * 10). It is a simple estimate from the share of the slot already booked, not a measured wait time. Slots are ordered by booked share (emptiest first), then start time.

### Example

```ts
import {
  Configuration,
  SuggestionsAndPriceWatchesApi,
} from 'payfound-sdk';
import type { PickupSuggestionsApiPickupSuggestionsGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new SuggestionsAndPriceWatchesApi(config);

  const body = {
    // string
    merchantId: merchantId_example,
    // Date
    day: 2013-10-20,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies PickupSuggestionsApiPickupSuggestionsGetRequest;

  try {
    const data = await api.pickupSuggestionsApiPickupSuggestionsGet(body);
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
| **day** | `Date` |  | [Defaults to `undefined`] |
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


## stockUpApiMerchantsMerchantIdStockUpPost

> any stockUpApiMerchantsMerchantIdStockUpPost(merchantId, authorization, xDemoRole, stockUpBody)

Stock Up

Projects demand for the next &#x60;days&#x60; days and drafts (never sends) a supplier email for products that will sell out.

### Example

```ts
import {
  Configuration,
  SuggestionsAndPriceWatchesApi,
} from 'payfound-sdk';
import type { StockUpApiMerchantsMerchantIdStockUpPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new SuggestionsAndPriceWatchesApi(config);

  const body = {
    // string
    merchantId: merchantId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
    // StockUpBody (optional)
    stockUpBody: ...,
  } satisfies StockUpApiMerchantsMerchantIdStockUpPostRequest;

  try {
    const data = await api.stockUpApiMerchantsMerchantIdStockUpPost(body);
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
| **stockUpBody** | [StockUpBody](StockUpBody.md) |  | [Optional] |

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

