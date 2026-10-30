# CatalogueApi

All URIs are relative to *http://127.0.0.1:8000*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**catalogueSummaryApiCatalogueSummaryGet**](CatalogueApi.md#cataloguesummaryapicataloguesummaryget) | **GET** /api/catalogue/summary | Catalogue Summary |



## catalogueSummaryApiCatalogueSummaryGet

> any catalogueSummaryApiCatalogueSummaryGet()

Catalogue Summary

### Example

```ts
import {
  Configuration,
  CatalogueApi,
} from 'payfound-sdk';
import type { CatalogueSummaryApiCatalogueSummaryGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new CatalogueApi(config);

  try {
    const data = await api.catalogueSummaryApiCatalogueSummaryGet();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

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

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

