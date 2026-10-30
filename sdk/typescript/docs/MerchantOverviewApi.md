# MerchantOverviewApi

All URIs are relative to *http://127.0.0.1:8000*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**analyticsApiMerchantAnalyticsGet**](MerchantOverviewApi.md#analyticsapimerchantanalyticsget) | **GET** /api/merchant/analytics | Analytics |
| [**forecastApiMerchantForecastGet**](MerchantOverviewApi.md#forecastapimerchantforecastget) | **GET** /api/merchant/forecast | Forecast |



## analyticsApiMerchantAnalyticsGet

> any analyticsApiMerchantAnalyticsGet(merchantId, days, lowStockThreshold, authorization, xDemoRole)

Analytics

### Example

```ts
import {
  Configuration,
  MerchantOverviewApi,
} from 'payfound-sdk';
import type { AnalyticsApiMerchantAnalyticsGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantOverviewApi(config);

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
  } satisfies AnalyticsApiMerchantAnalyticsGetRequest;

  try {
    const data = await api.analyticsApiMerchantAnalyticsGet(body);
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


## forecastApiMerchantForecastGet

> any forecastApiMerchantForecastGet(merchantId, authorization, xDemoRole)

Forecast

### Example

```ts
import {
  Configuration,
  MerchantOverviewApi,
} from 'payfound-sdk';
import type { ForecastApiMerchantForecastGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantOverviewApi(config);

  const body = {
    // string
    merchantId: merchantId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies ForecastApiMerchantForecastGetRequest;

  try {
    const data = await api.forecastApiMerchantForecastGet(body);
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

