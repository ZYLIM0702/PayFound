# MerchantApi

All URIs are relative to *http://127.0.0.1:8000*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**acceptStaffApiMerchantStaffInvitationsInvitationIdAcceptPost**](MerchantApi.md#acceptstaffapimerchantstaffinvitationsinvitationidacceptpost) | **POST** /api/merchant/staff/invitations/{invitation_id}/accept | Accept Staff |
| [**connectApiMerchantConnectionsPost**](MerchantApi.md#connectapimerchantconnectionspost) | **POST** /api/merchant/connections | Connect |
| [**connectionsApiMerchantConnectionsGet**](MerchantApi.md#connectionsapimerchantconnectionsget) | **GET** /api/merchant/connections | Connections |
| [**createLocationApiMerchantLocationsPost**](MerchantApi.md#createlocationapimerchantlocationspost) | **POST** /api/merchant/locations | Create Location |
| [**createPickupSlotApiMerchantPickupSlotsPost**](MerchantApi.md#createpickupslotapimerchantpickupslotspost) | **POST** /api/merchant/pickup-slots | Create Pickup Slot |
| [**createProductApiMerchantProductsPost**](MerchantApi.md#createproductapimerchantproductspost) | **POST** /api/merchant/products | Create Product |
| [**createReportApiMerchantReportsPost**](MerchantApi.md#createreportapimerchantreportspost) | **POST** /api/merchant/reports | Create Report |
| [**dashboardApiMerchantDashboardGet**](MerchantApi.md#dashboardapimerchantdashboardget) | **GET** /api/merchant/dashboard | Dashboard |
| [**deleteReportApiMerchantReportsReportIdDelete**](MerchantApi.md#deletereportapimerchantreportsreportiddelete) | **DELETE** /api/merchant/reports/{report_id} | Delete Report |
| [**disconnectApiMerchantConnectionsConnectionIdDelete**](MerchantApi.md#disconnectapimerchantconnectionsconnectioniddelete) | **DELETE** /api/merchant/connections/{connection_id} | Disconnect |
| [**editStockApiMerchantProductsProductIdStockPatch**](MerchantApi.md#editstockapimerchantproductsproductidstockpatch) | **PATCH** /api/merchant/products/{product_id}/stock | Edit Stock |
| [**editStoreStatusApiMerchantStatusPatch**](MerchantApi.md#editstorestatusapimerchantstatuspatch) | **PATCH** /api/merchant/status | Edit Store Status |
| [**getConsentApiMerchantAiConsentGet**](MerchantApi.md#getconsentapimerchantaiconsentget) | **GET** /api/merchant/ai-consent | Get Consent |
| [**inviteStaffApiMerchantStaffPost**](MerchantApi.md#invitestaffapimerchantstaffpost) | **POST** /api/merchant/staff | Invite Staff |
| [**listReportsApiMerchantReportsGet**](MerchantApi.md#listreportsapimerchantreportsget) | **GET** /api/merchant/reports | List Reports |
| [**listStaffApiMerchantStaffGet**](MerchantApi.md#liststaffapimerchantstaffget) | **GET** /api/merchant/staff | List Staff |
| [**merchantLocationsApiMerchantLocationsGet**](MerchantApi.md#merchantlocationsapimerchantlocationsget) | **GET** /api/merchant/locations | Merchant Locations |
| [**merchantProfileApiMerchantProfileGet**](MerchantApi.md#merchantprofileapimerchantprofileget) | **GET** /api/merchant/profile | Merchant Profile |
| [**onboardApiMerchantOnboardPost**](MerchantApi.md#onboardapimerchantonboardpost) | **POST** /api/merchant/onboard | Onboard |
| [**patchLocationApiMerchantLocationsLocationIdPatch**](MerchantApi.md#patchlocationapimerchantlocationslocationidpatch) | **PATCH** /api/merchant/locations/{location_id} | Patch Location |
| [**patchProfileApiMerchantProfilePatch**](MerchantApi.md#patchprofileapimerchantprofilepatch) | **PATCH** /api/merchant/profile | Patch Profile |
| [**pickupCalendarApiMerchantPickupSlotsGet**](MerchantApi.md#pickupcalendarapimerchantpickupslotsget) | **GET** /api/merchant/pickup-slots | Pickup Calendar |
| [**publishApiMerchantConnectionsConnectionIdPublishPost**](MerchantApi.md#publishapimerchantconnectionsconnectionidpublishpost) | **POST** /api/merchant/connections/{connection_id}/publish | Publish |
| [**reauthorizeApiMerchantConnectionsConnectionIdAuthorizePost**](MerchantApi.md#reauthorizeapimerchantconnectionsconnectionidauthorizepost) | **POST** /api/merchant/connections/{connection_id}/authorize | Reauthorize |
| [**registerHooksApiMerchantConnectionsConnectionIdWebhooksPost**](MerchantApi.md#registerhooksapimerchantconnectionsconnectionidwebhookspost) | **POST** /api/merchant/connections/{connection_id}/webhooks | Register Hooks |
| [**revokeStaffApiMerchantStaffMembershipIdDelete**](MerchantApi.md#revokestaffapimerchantstaffmembershipiddelete) | **DELETE** /api/merchant/staff/{membership_id} | Revoke Staff |
| [**runsApiMerchantConnectionsConnectionIdRunsGet**](MerchantApi.md#runsapimerchantconnectionsconnectionidrunsget) | **GET** /api/merchant/connections/{connection_id}/runs | Runs |
| [**setConsentApiMerchantAiConsentPost**](MerchantApi.md#setconsentapimerchantaiconsentpost) | **POST** /api/merchant/ai-consent | Set Consent |
| [**sourceLocationsApiMerchantConnectionsConnectionIdLocationsGet**](MerchantApi.md#sourcelocationsapimerchantconnectionsconnectionidlocationsget) | **GET** /api/merchant/connections/{connection_id}/locations | Source Locations |
| [**syncApiMerchantConnectionsConnectionIdSyncPost**](MerchantApi.md#syncapimerchantconnectionsconnectionidsyncpost) | **POST** /api/merchant/connections/{connection_id}/sync | Sync |
| [**updateReportApiMerchantReportsReportIdPut**](MerchantApi.md#updatereportapimerchantreportsreportidput) | **PUT** /api/merchant/reports/{report_id} | Update Report |



## acceptStaffApiMerchantStaffInvitationsInvitationIdAcceptPost

> any acceptStaffApiMerchantStaffInvitationsInvitationIdAcceptPost(invitationId, authorization, xDemoRole)

Accept Staff

### Example

```ts
import {
  Configuration,
  MerchantApi,
} from 'payfound-sdk';
import type { AcceptStaffApiMerchantStaffInvitationsInvitationIdAcceptPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantApi(config);

  const body = {
    // string
    invitationId: invitationId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies AcceptStaffApiMerchantStaffInvitationsInvitationIdAcceptPostRequest;

  try {
    const data = await api.acceptStaffApiMerchantStaffInvitationsInvitationIdAcceptPost(body);
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
| **invitationId** | `string` |  | [Defaults to `undefined`] |
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


## connectApiMerchantConnectionsPost

> any connectApiMerchantConnectionsPost(appConnectorsRoutesConnectInput, authorization, xDemoRole)

Connect

### Example

```ts
import {
  Configuration,
  MerchantApi,
} from 'payfound-sdk';
import type { ConnectApiMerchantConnectionsPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantApi(config);

  const body = {
    // AppConnectorsRoutesConnectInput
    appConnectorsRoutesConnectInput: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies ConnectApiMerchantConnectionsPostRequest;

  try {
    const data = await api.connectApiMerchantConnectionsPost(body);
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
| **appConnectorsRoutesConnectInput** | [AppConnectorsRoutesConnectInput](AppConnectorsRoutesConnectInput.md) |  | |
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


## connectionsApiMerchantConnectionsGet

> any connectionsApiMerchantConnectionsGet(merchantId, authorization, xDemoRole)

Connections

### Example

```ts
import {
  Configuration,
  MerchantApi,
} from 'payfound-sdk';
import type { ConnectionsApiMerchantConnectionsGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantApi(config);

  const body = {
    // string
    merchantId: merchantId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies ConnectionsApiMerchantConnectionsGetRequest;

  try {
    const data = await api.connectionsApiMerchantConnectionsGet(body);
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


## createLocationApiMerchantLocationsPost

> any createLocationApiMerchantLocationsPost(locationInput, merchantId, authorization, xDemoRole)

Create Location

### Example

```ts
import {
  Configuration,
  MerchantApi,
} from 'payfound-sdk';
import type { CreateLocationApiMerchantLocationsPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantApi(config);

  const body = {
    // LocationInput
    locationInput: ...,
    // string (optional)
    merchantId: merchantId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies CreateLocationApiMerchantLocationsPostRequest;

  try {
    const data = await api.createLocationApiMerchantLocationsPost(body);
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
| **locationInput** | [LocationInput](LocationInput.md) |  | |
| **merchantId** | `string` |  | [Optional] [Defaults to `undefined`] |
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


## createPickupSlotApiMerchantPickupSlotsPost

> any createPickupSlotApiMerchantPickupSlotsPost(slotInput, authorization, xDemoRole)

Create Pickup Slot

### Example

```ts
import {
  Configuration,
  MerchantApi,
} from 'payfound-sdk';
import type { CreatePickupSlotApiMerchantPickupSlotsPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantApi(config);

  const body = {
    // SlotInput
    slotInput: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies CreatePickupSlotApiMerchantPickupSlotsPostRequest;

  try {
    const data = await api.createPickupSlotApiMerchantPickupSlotsPost(body);
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
| **slotInput** | [SlotInput](SlotInput.md) |  | |
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


## createProductApiMerchantProductsPost

> any createProductApiMerchantProductsPost(merchantId, productInput, authorization, xDemoRole)

Create Product

### Example

```ts
import {
  Configuration,
  MerchantApi,
} from 'payfound-sdk';
import type { CreateProductApiMerchantProductsPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantApi(config);

  const body = {
    // string
    merchantId: merchantId_example,
    // ProductInput
    productInput: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies CreateProductApiMerchantProductsPostRequest;

  try {
    const data = await api.createProductApiMerchantProductsPost(body);
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
| **productInput** | [ProductInput](ProductInput.md) |  | |
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


## createReportApiMerchantReportsPost

> any createReportApiMerchantReportsPost(reportCreate, authorization, xDemoRole)

Create Report

### Example

```ts
import {
  Configuration,
  MerchantApi,
} from 'payfound-sdk';
import type { CreateReportApiMerchantReportsPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantApi(config);

  const body = {
    // ReportCreate
    reportCreate: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies CreateReportApiMerchantReportsPostRequest;

  try {
    const data = await api.createReportApiMerchantReportsPost(body);
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
| **reportCreate** | [ReportCreate](ReportCreate.md) |  | |
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


## dashboardApiMerchantDashboardGet

> any dashboardApiMerchantDashboardGet(merchantId, authorization, xDemoRole)

Dashboard

### Example

```ts
import {
  Configuration,
  MerchantApi,
} from 'payfound-sdk';
import type { DashboardApiMerchantDashboardGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantApi(config);

  const body = {
    // string (optional)
    merchantId: merchantId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies DashboardApiMerchantDashboardGetRequest;

  try {
    const data = await api.dashboardApiMerchantDashboardGet(body);
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
| **merchantId** | `string` |  | [Optional] [Defaults to `undefined`] |
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


## deleteReportApiMerchantReportsReportIdDelete

> deleteReportApiMerchantReportsReportIdDelete(reportId, version, authorization, xDemoRole)

Delete Report

### Example

```ts
import {
  Configuration,
  MerchantApi,
} from 'payfound-sdk';
import type { DeleteReportApiMerchantReportsReportIdDeleteRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantApi(config);

  const body = {
    // string
    reportId: reportId_example,
    // number (optional)
    version: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies DeleteReportApiMerchantReportsReportIdDeleteRequest;

  try {
    const data = await api.deleteReportApiMerchantReportsReportIdDelete(body);
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
| **reportId** | `string` |  | [Defaults to `undefined`] |
| **version** | `number` |  | [Optional] [Defaults to `undefined`] |
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


## disconnectApiMerchantConnectionsConnectionIdDelete

> any disconnectApiMerchantConnectionsConnectionIdDelete(connectionId, authorization, xDemoRole)

Disconnect

### Example

```ts
import {
  Configuration,
  MerchantApi,
} from 'payfound-sdk';
import type { DisconnectApiMerchantConnectionsConnectionIdDeleteRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantApi(config);

  const body = {
    // string
    connectionId: connectionId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies DisconnectApiMerchantConnectionsConnectionIdDeleteRequest;

  try {
    const data = await api.disconnectApiMerchantConnectionsConnectionIdDelete(body);
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
| **connectionId** | `string` |  | [Defaults to `undefined`] |
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


## editStockApiMerchantProductsProductIdStockPatch

> any editStockApiMerchantProductsProductIdStockPatch(productId, stockUpdate, authorization, xDemoRole)

Edit Stock

### Example

```ts
import {
  Configuration,
  MerchantApi,
} from 'payfound-sdk';
import type { EditStockApiMerchantProductsProductIdStockPatchRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantApi(config);

  const body = {
    // string
    productId: productId_example,
    // StockUpdate
    stockUpdate: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies EditStockApiMerchantProductsProductIdStockPatchRequest;

  try {
    const data = await api.editStockApiMerchantProductsProductIdStockPatch(body);
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
| **productId** | `string` |  | [Defaults to `undefined`] |
| **stockUpdate** | [StockUpdate](StockUpdate.md) |  | |
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


## editStoreStatusApiMerchantStatusPatch

> any editStoreStatusApiMerchantStatusPatch(merchantStatus, merchantId, authorization, xDemoRole)

Edit Store Status

### Example

```ts
import {
  Configuration,
  MerchantApi,
} from 'payfound-sdk';
import type { EditStoreStatusApiMerchantStatusPatchRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantApi(config);

  const body = {
    // MerchantStatus
    merchantStatus: ...,
    // string (optional)
    merchantId: merchantId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies EditStoreStatusApiMerchantStatusPatchRequest;

  try {
    const data = await api.editStoreStatusApiMerchantStatusPatch(body);
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
| **merchantStatus** | [MerchantStatus](MerchantStatus.md) |  | |
| **merchantId** | `string` |  | [Optional] [Defaults to `undefined`] |
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


## getConsentApiMerchantAiConsentGet

> any getConsentApiMerchantAiConsentGet(merchantId, authorization, xDemoRole)

Get Consent

### Example

```ts
import {
  Configuration,
  MerchantApi,
} from 'payfound-sdk';
import type { GetConsentApiMerchantAiConsentGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantApi(config);

  const body = {
    // string (optional)
    merchantId: merchantId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies GetConsentApiMerchantAiConsentGetRequest;

  try {
    const data = await api.getConsentApiMerchantAiConsentGet(body);
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
| **merchantId** | `string` |  | [Optional] [Defaults to `undefined`] |
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


## inviteStaffApiMerchantStaffPost

> any inviteStaffApiMerchantStaffPost(staffInput, merchantId, authorization, xDemoRole)

Invite Staff

### Example

```ts
import {
  Configuration,
  MerchantApi,
} from 'payfound-sdk';
import type { InviteStaffApiMerchantStaffPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantApi(config);

  const body = {
    // StaffInput
    staffInput: ...,
    // string (optional)
    merchantId: merchantId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies InviteStaffApiMerchantStaffPostRequest;

  try {
    const data = await api.inviteStaffApiMerchantStaffPost(body);
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
| **staffInput** | [StaffInput](StaffInput.md) |  | |
| **merchantId** | `string` |  | [Optional] [Defaults to `undefined`] |
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


## listReportsApiMerchantReportsGet

> any listReportsApiMerchantReportsGet(merchantId, authorization, xDemoRole)

List Reports

### Example

```ts
import {
  Configuration,
  MerchantApi,
} from 'payfound-sdk';
import type { ListReportsApiMerchantReportsGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantApi(config);

  const body = {
    // string (optional)
    merchantId: merchantId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies ListReportsApiMerchantReportsGetRequest;

  try {
    const data = await api.listReportsApiMerchantReportsGet(body);
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
| **merchantId** | `string` |  | [Optional] [Defaults to `undefined`] |
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


## listStaffApiMerchantStaffGet

> any listStaffApiMerchantStaffGet(merchantId, authorization, xDemoRole)

List Staff

### Example

```ts
import {
  Configuration,
  MerchantApi,
} from 'payfound-sdk';
import type { ListStaffApiMerchantStaffGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantApi(config);

  const body = {
    // string (optional)
    merchantId: merchantId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies ListStaffApiMerchantStaffGetRequest;

  try {
    const data = await api.listStaffApiMerchantStaffGet(body);
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
| **merchantId** | `string` |  | [Optional] [Defaults to `undefined`] |
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


## merchantLocationsApiMerchantLocationsGet

> any merchantLocationsApiMerchantLocationsGet(merchantId, authorization, xDemoRole)

Merchant Locations

### Example

```ts
import {
  Configuration,
  MerchantApi,
} from 'payfound-sdk';
import type { MerchantLocationsApiMerchantLocationsGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantApi(config);

  const body = {
    // string (optional)
    merchantId: merchantId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies MerchantLocationsApiMerchantLocationsGetRequest;

  try {
    const data = await api.merchantLocationsApiMerchantLocationsGet(body);
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
| **merchantId** | `string` |  | [Optional] [Defaults to `undefined`] |
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


## merchantProfileApiMerchantProfileGet

> any merchantProfileApiMerchantProfileGet(merchantId, authorization, xDemoRole)

Merchant Profile

### Example

```ts
import {
  Configuration,
  MerchantApi,
} from 'payfound-sdk';
import type { MerchantProfileApiMerchantProfileGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantApi(config);

  const body = {
    // string (optional)
    merchantId: merchantId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies MerchantProfileApiMerchantProfileGetRequest;

  try {
    const data = await api.merchantProfileApiMerchantProfileGet(body);
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
| **merchantId** | `string` |  | [Optional] [Defaults to `undefined`] |
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


## onboardApiMerchantOnboardPost

> any onboardApiMerchantOnboardPost(onboardInput, authorization, xDemoRole)

Onboard

### Example

```ts
import {
  Configuration,
  MerchantApi,
} from 'payfound-sdk';
import type { OnboardApiMerchantOnboardPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantApi(config);

  const body = {
    // OnboardInput
    onboardInput: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies OnboardApiMerchantOnboardPostRequest;

  try {
    const data = await api.onboardApiMerchantOnboardPost(body);
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
| **onboardInput** | [OnboardInput](OnboardInput.md) |  | |
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


## patchLocationApiMerchantLocationsLocationIdPatch

> any patchLocationApiMerchantLocationsLocationIdPatch(locationId, locationPatch, authorization, xDemoRole)

Patch Location

### Example

```ts
import {
  Configuration,
  MerchantApi,
} from 'payfound-sdk';
import type { PatchLocationApiMerchantLocationsLocationIdPatchRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantApi(config);

  const body = {
    // string
    locationId: locationId_example,
    // LocationPatch
    locationPatch: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies PatchLocationApiMerchantLocationsLocationIdPatchRequest;

  try {
    const data = await api.patchLocationApiMerchantLocationsLocationIdPatch(body);
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
| **locationId** | `string` |  | [Defaults to `undefined`] |
| **locationPatch** | [LocationPatch](LocationPatch.md) |  | |
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


## patchProfileApiMerchantProfilePatch

> any patchProfileApiMerchantProfilePatch(profilePatch, merchantId, authorization, xDemoRole)

Patch Profile

### Example

```ts
import {
  Configuration,
  MerchantApi,
} from 'payfound-sdk';
import type { PatchProfileApiMerchantProfilePatchRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantApi(config);

  const body = {
    // ProfilePatch
    profilePatch: ...,
    // string (optional)
    merchantId: merchantId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies PatchProfileApiMerchantProfilePatchRequest;

  try {
    const data = await api.patchProfileApiMerchantProfilePatch(body);
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
| **profilePatch** | [ProfilePatch](ProfilePatch.md) |  | |
| **merchantId** | `string` |  | [Optional] [Defaults to `undefined`] |
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


## pickupCalendarApiMerchantPickupSlotsGet

> any pickupCalendarApiMerchantPickupSlotsGet(startAt, endAt, merchantId, authorization, xDemoRole)

Pickup Calendar

### Example

```ts
import {
  Configuration,
  MerchantApi,
} from 'payfound-sdk';
import type { PickupCalendarApiMerchantPickupSlotsGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantApi(config);

  const body = {
    // Date
    startAt: 2013-10-20T19:20:30+01:00,
    // Date
    endAt: 2013-10-20T19:20:30+01:00,
    // string (optional)
    merchantId: merchantId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies PickupCalendarApiMerchantPickupSlotsGetRequest;

  try {
    const data = await api.pickupCalendarApiMerchantPickupSlotsGet(body);
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
| **startAt** | `Date` |  | [Defaults to `undefined`] |
| **endAt** | `Date` |  | [Defaults to `undefined`] |
| **merchantId** | `string` |  | [Optional] [Defaults to `undefined`] |
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


## publishApiMerchantConnectionsConnectionIdPublishPost

> any publishApiMerchantConnectionsConnectionIdPublishPost(connectionId, publishInput, authorization, xDemoRole)

Publish

### Example

```ts
import {
  Configuration,
  MerchantApi,
} from 'payfound-sdk';
import type { PublishApiMerchantConnectionsConnectionIdPublishPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantApi(config);

  const body = {
    // string
    connectionId: connectionId_example,
    // PublishInput
    publishInput: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies PublishApiMerchantConnectionsConnectionIdPublishPostRequest;

  try {
    const data = await api.publishApiMerchantConnectionsConnectionIdPublishPost(body);
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
| **connectionId** | `string` |  | [Defaults to `undefined`] |
| **publishInput** | [PublishInput](PublishInput.md) |  | |
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


## reauthorizeApiMerchantConnectionsConnectionIdAuthorizePost

> any reauthorizeApiMerchantConnectionsConnectionIdAuthorizePost(connectionId, authorization, xDemoRole)

Reauthorize

### Example

```ts
import {
  Configuration,
  MerchantApi,
} from 'payfound-sdk';
import type { ReauthorizeApiMerchantConnectionsConnectionIdAuthorizePostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantApi(config);

  const body = {
    // string
    connectionId: connectionId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies ReauthorizeApiMerchantConnectionsConnectionIdAuthorizePostRequest;

  try {
    const data = await api.reauthorizeApiMerchantConnectionsConnectionIdAuthorizePost(body);
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
| **connectionId** | `string` |  | [Defaults to `undefined`] |
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


## registerHooksApiMerchantConnectionsConnectionIdWebhooksPost

> any registerHooksApiMerchantConnectionsConnectionIdWebhooksPost(connectionId, authorization, xDemoRole)

Register Hooks

### Example

```ts
import {
  Configuration,
  MerchantApi,
} from 'payfound-sdk';
import type { RegisterHooksApiMerchantConnectionsConnectionIdWebhooksPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantApi(config);

  const body = {
    // string
    connectionId: connectionId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies RegisterHooksApiMerchantConnectionsConnectionIdWebhooksPostRequest;

  try {
    const data = await api.registerHooksApiMerchantConnectionsConnectionIdWebhooksPost(body);
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
| **connectionId** | `string` |  | [Defaults to `undefined`] |
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


## revokeStaffApiMerchantStaffMembershipIdDelete

> any revokeStaffApiMerchantStaffMembershipIdDelete(membershipId, authorization, xDemoRole)

Revoke Staff

### Example

```ts
import {
  Configuration,
  MerchantApi,
} from 'payfound-sdk';
import type { RevokeStaffApiMerchantStaffMembershipIdDeleteRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantApi(config);

  const body = {
    // string
    membershipId: membershipId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies RevokeStaffApiMerchantStaffMembershipIdDeleteRequest;

  try {
    const data = await api.revokeStaffApiMerchantStaffMembershipIdDelete(body);
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
| **membershipId** | `string` |  | [Defaults to `undefined`] |
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


## runsApiMerchantConnectionsConnectionIdRunsGet

> any runsApiMerchantConnectionsConnectionIdRunsGet(connectionId, authorization, xDemoRole)

Runs

### Example

```ts
import {
  Configuration,
  MerchantApi,
} from 'payfound-sdk';
import type { RunsApiMerchantConnectionsConnectionIdRunsGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantApi(config);

  const body = {
    // string
    connectionId: connectionId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies RunsApiMerchantConnectionsConnectionIdRunsGetRequest;

  try {
    const data = await api.runsApiMerchantConnectionsConnectionIdRunsGet(body);
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
| **connectionId** | `string` |  | [Defaults to `undefined`] |
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


## setConsentApiMerchantAiConsentPost

> any setConsentApiMerchantAiConsentPost(merchantId, consentInput, authorization, xDemoRole)

Set Consent

### Example

```ts
import {
  Configuration,
  MerchantApi,
} from 'payfound-sdk';
import type { SetConsentApiMerchantAiConsentPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantApi(config);

  const body = {
    // string
    merchantId: merchantId_example,
    // ConsentInput
    consentInput: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies SetConsentApiMerchantAiConsentPostRequest;

  try {
    const data = await api.setConsentApiMerchantAiConsentPost(body);
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
| **consentInput** | [ConsentInput](ConsentInput.md) |  | |
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


## sourceLocationsApiMerchantConnectionsConnectionIdLocationsGet

> any sourceLocationsApiMerchantConnectionsConnectionIdLocationsGet(connectionId, authorization, xDemoRole)

Source Locations

### Example

```ts
import {
  Configuration,
  MerchantApi,
} from 'payfound-sdk';
import type { SourceLocationsApiMerchantConnectionsConnectionIdLocationsGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantApi(config);

  const body = {
    // string
    connectionId: connectionId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies SourceLocationsApiMerchantConnectionsConnectionIdLocationsGetRequest;

  try {
    const data = await api.sourceLocationsApiMerchantConnectionsConnectionIdLocationsGet(body);
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
| **connectionId** | `string` |  | [Defaults to `undefined`] |
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


## syncApiMerchantConnectionsConnectionIdSyncPost

> any syncApiMerchantConnectionsConnectionIdSyncPost(connectionId, authorization, xDemoRole)

Sync

### Example

```ts
import {
  Configuration,
  MerchantApi,
} from 'payfound-sdk';
import type { SyncApiMerchantConnectionsConnectionIdSyncPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantApi(config);

  const body = {
    // string
    connectionId: connectionId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies SyncApiMerchantConnectionsConnectionIdSyncPostRequest;

  try {
    const data = await api.syncApiMerchantConnectionsConnectionIdSyncPost(body);
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
| **connectionId** | `string` |  | [Defaults to `undefined`] |
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


## updateReportApiMerchantReportsReportIdPut

> any updateReportApiMerchantReportsReportIdPut(reportId, reportUpdate, authorization, xDemoRole)

Update Report

### Example

```ts
import {
  Configuration,
  MerchantApi,
} from 'payfound-sdk';
import type { UpdateReportApiMerchantReportsReportIdPutRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new MerchantApi(config);

  const body = {
    // string
    reportId: reportId_example,
    // ReportUpdate
    reportUpdate: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies UpdateReportApiMerchantReportsReportIdPutRequest;

  try {
    const data = await api.updateReportApiMerchantReportsReportIdPut(body);
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
| **reportId** | `string` |  | [Defaults to `undefined`] |
| **reportUpdate** | [ReportUpdate](ReportUpdate.md) |  | |
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

