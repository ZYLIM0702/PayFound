# OrdersApi

All URIs are relative to *http://127.0.0.1:8000*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**bookPickupApiOrdersOrderIdPickupPost**](OrdersApi.md#bookpickupapiordersorderidpickuppost) | **POST** /api/orders/{order_id}/pickup | Book Pickup |
| [**cancelReservationApiOrdersOrderIdCancelPost**](OrdersApi.md#cancelreservationapiordersorderidcancelpost) | **POST** /api/orders/{order_id}/cancel | Cancel Reservation |
| [**confirmOrderApiOrdersOrderIdConfirmPost**](OrdersApi.md#confirmorderapiordersorderidconfirmpost) | **POST** /api/orders/{order_id}/confirm | Confirm Order |
| [**confirmPickupApiOrdersOrderIdConfirmPickupPost**](OrdersApi.md#confirmpickupapiordersorderidconfirmpickuppost) | **POST** /api/orders/{order_id}/confirm-pickup | Confirm Pickup |
| [**detailOrderApiOrdersOrderIdGet**](OrdersApi.md#detailorderapiordersorderidget) | **GET** /api/orders/{order_id} | Detail Order |
| [**fulfilApiOrdersOrderIdFulfilmentPost**](OrdersApi.md#fulfilapiordersorderidfulfilmentpost) | **POST** /api/orders/{order_id}/fulfilment | Fulfil |
| [**listOrdersApiOrdersGet**](OrdersApi.md#listordersapiordersget) | **GET** /api/orders | List Orders |
| [**mockPaymentApiOrdersOrderIdMockPayPost**](OrdersApi.md#mockpaymentapiordersorderidmockpaypost) | **POST** /api/orders/{order_id}/mock-pay | Mock Payment |
| [**orderInvoiceApiOrdersOrderIdInvoiceGet**](OrdersApi.md#orderinvoiceapiordersorderidinvoiceget) | **GET** /api/orders/{order_id}/invoice | Order Invoice |
| [**paypalCaptureApiOrdersOrderIdPaypalCapturePost**](OrdersApi.md#paypalcaptureapiordersorderidpaypalcapturepost) | **POST** /api/orders/{order_id}/paypal/capture | Paypal Capture |
| [**paypalCreateApiOrdersOrderIdPaypalCreatePost**](OrdersApi.md#paypalcreateapiordersorderidpaypalcreatepost) | **POST** /api/orders/{order_id}/paypal/create | Paypal Create |
| [**paypalReconcileApiOrdersOrderIdPaypalReconcilePost**](OrdersApi.md#paypalreconcileapiordersorderidpaypalreconcilepost) | **POST** /api/orders/{order_id}/paypal/reconcile | Paypal Reconcile |
| [**paypalRestartApiOrdersOrderIdPaypalRestartPost**](OrdersApi.md#paypalrestartapiordersorderidpaypalrestartpost) | **POST** /api/orders/{order_id}/paypal/restart | Paypal Restart |
| [**paypalResumeApiOrdersOrderIdPaypalResumePost**](OrdersApi.md#paypalresumeapiordersorderidpaypalresumepost) | **POST** /api/orders/{order_id}/paypal/resume | Paypal Resume |
| [**refundApiOrdersOrderIdRefundPost**](OrdersApi.md#refundapiordersorderidrefundpost) | **POST** /api/orders/{order_id}/refund | Refund |
| [**reserveApiOrdersReservePost**](OrdersApi.md#reserveapiordersreservepost) | **POST** /api/orders/reserve | Reserve |



## bookPickupApiOrdersOrderIdPickupPost

> any bookPickupApiOrdersOrderIdPickupPost(orderId, bookingInput, authorization, xDemoRole)

Book Pickup

### Example

```ts
import {
  Configuration,
  OrdersApi,
} from 'payfound-sdk';
import type { BookPickupApiOrdersOrderIdPickupPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new OrdersApi(config);

  const body = {
    // string
    orderId: orderId_example,
    // BookingInput
    bookingInput: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies BookPickupApiOrdersOrderIdPickupPostRequest;

  try {
    const data = await api.bookPickupApiOrdersOrderIdPickupPost(body);
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
| **orderId** | `string` |  | [Defaults to `undefined`] |
| **bookingInput** | [BookingInput](BookingInput.md) |  | |
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


## cancelReservationApiOrdersOrderIdCancelPost

> any cancelReservationApiOrdersOrderIdCancelPost(orderId, authorization, xDemoRole)

Cancel Reservation

### Example

```ts
import {
  Configuration,
  OrdersApi,
} from 'payfound-sdk';
import type { CancelReservationApiOrdersOrderIdCancelPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new OrdersApi(config);

  const body = {
    // string
    orderId: orderId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies CancelReservationApiOrdersOrderIdCancelPostRequest;

  try {
    const data = await api.cancelReservationApiOrdersOrderIdCancelPost(body);
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


## confirmOrderApiOrdersOrderIdConfirmPost

> any confirmOrderApiOrdersOrderIdConfirmPost(orderId, authorization, xDemoRole)

Confirm Order

### Example

```ts
import {
  Configuration,
  OrdersApi,
} from 'payfound-sdk';
import type { ConfirmOrderApiOrdersOrderIdConfirmPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new OrdersApi(config);

  const body = {
    // string
    orderId: orderId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies ConfirmOrderApiOrdersOrderIdConfirmPostRequest;

  try {
    const data = await api.confirmOrderApiOrdersOrderIdConfirmPost(body);
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


## confirmPickupApiOrdersOrderIdConfirmPickupPost

> any confirmPickupApiOrdersOrderIdConfirmPickupPost(orderId, authorization, xDemoRole)

Confirm Pickup

### Example

```ts
import {
  Configuration,
  OrdersApi,
} from 'payfound-sdk';
import type { ConfirmPickupApiOrdersOrderIdConfirmPickupPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new OrdersApi(config);

  const body = {
    // string
    orderId: orderId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies ConfirmPickupApiOrdersOrderIdConfirmPickupPostRequest;

  try {
    const data = await api.confirmPickupApiOrdersOrderIdConfirmPickupPost(body);
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


## detailOrderApiOrdersOrderIdGet

> any detailOrderApiOrdersOrderIdGet(orderId, authorization, xDemoRole)

Detail Order

### Example

```ts
import {
  Configuration,
  OrdersApi,
} from 'payfound-sdk';
import type { DetailOrderApiOrdersOrderIdGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new OrdersApi(config);

  const body = {
    // string
    orderId: orderId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies DetailOrderApiOrdersOrderIdGetRequest;

  try {
    const data = await api.detailOrderApiOrdersOrderIdGet(body);
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


## fulfilApiOrdersOrderIdFulfilmentPost

> any fulfilApiOrdersOrderIdFulfilmentPost(orderId, statusUpdate, authorization, xDemoRole)

Fulfil

### Example

```ts
import {
  Configuration,
  OrdersApi,
} from 'payfound-sdk';
import type { FulfilApiOrdersOrderIdFulfilmentPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new OrdersApi(config);

  const body = {
    // string
    orderId: orderId_example,
    // StatusUpdate
    statusUpdate: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies FulfilApiOrdersOrderIdFulfilmentPostRequest;

  try {
    const data = await api.fulfilApiOrdersOrderIdFulfilmentPost(body);
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
| **orderId** | `string` |  | [Defaults to `undefined`] |
| **statusUpdate** | [StatusUpdate](StatusUpdate.md) |  | |
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


## listOrdersApiOrdersGet

> any listOrdersApiOrdersGet(merchantId, limit, offset, authorization, xDemoRole)

List Orders

### Example

```ts
import {
  Configuration,
  OrdersApi,
} from 'payfound-sdk';
import type { ListOrdersApiOrdersGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new OrdersApi(config);

  const body = {
    // string (optional)
    merchantId: merchantId_example,
    // number (optional)
    limit: 56,
    // number (optional)
    offset: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies ListOrdersApiOrdersGetRequest;

  try {
    const data = await api.listOrdersApiOrdersGet(body);
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
| **limit** | `number` |  | [Optional] [Defaults to `200`] |
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


## mockPaymentApiOrdersOrderIdMockPayPost

> any mockPaymentApiOrdersOrderIdMockPayPost(orderId, authorization, xDemoRole)

Mock Payment

### Example

```ts
import {
  Configuration,
  OrdersApi,
} from 'payfound-sdk';
import type { MockPaymentApiOrdersOrderIdMockPayPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new OrdersApi(config);

  const body = {
    // string
    orderId: orderId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies MockPaymentApiOrdersOrderIdMockPayPostRequest;

  try {
    const data = await api.mockPaymentApiOrdersOrderIdMockPayPost(body);
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


## orderInvoiceApiOrdersOrderIdInvoiceGet

> any orderInvoiceApiOrdersOrderIdInvoiceGet(orderId, authorization, xDemoRole)

Order Invoice

### Example

```ts
import {
  Configuration,
  OrdersApi,
} from 'payfound-sdk';
import type { OrderInvoiceApiOrdersOrderIdInvoiceGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new OrdersApi(config);

  const body = {
    // string
    orderId: orderId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies OrderInvoiceApiOrdersOrderIdInvoiceGetRequest;

  try {
    const data = await api.orderInvoiceApiOrdersOrderIdInvoiceGet(body);
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


## paypalCaptureApiOrdersOrderIdPaypalCapturePost

> any paypalCaptureApiOrdersOrderIdPaypalCapturePost(orderId, authorization, xDemoRole)

Paypal Capture

### Example

```ts
import {
  Configuration,
  OrdersApi,
} from 'payfound-sdk';
import type { PaypalCaptureApiOrdersOrderIdPaypalCapturePostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new OrdersApi(config);

  const body = {
    // string
    orderId: orderId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies PaypalCaptureApiOrdersOrderIdPaypalCapturePostRequest;

  try {
    const data = await api.paypalCaptureApiOrdersOrderIdPaypalCapturePost(body);
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


## paypalCreateApiOrdersOrderIdPaypalCreatePost

> any paypalCreateApiOrdersOrderIdPaypalCreatePost(orderId, authorization, xDemoRole)

Paypal Create

### Example

```ts
import {
  Configuration,
  OrdersApi,
} from 'payfound-sdk';
import type { PaypalCreateApiOrdersOrderIdPaypalCreatePostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new OrdersApi(config);

  const body = {
    // string
    orderId: orderId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies PaypalCreateApiOrdersOrderIdPaypalCreatePostRequest;

  try {
    const data = await api.paypalCreateApiOrdersOrderIdPaypalCreatePost(body);
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


## paypalReconcileApiOrdersOrderIdPaypalReconcilePost

> any paypalReconcileApiOrdersOrderIdPaypalReconcilePost(orderId, authorization, xDemoRole)

Paypal Reconcile

### Example

```ts
import {
  Configuration,
  OrdersApi,
} from 'payfound-sdk';
import type { PaypalReconcileApiOrdersOrderIdPaypalReconcilePostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new OrdersApi(config);

  const body = {
    // string
    orderId: orderId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies PaypalReconcileApiOrdersOrderIdPaypalReconcilePostRequest;

  try {
    const data = await api.paypalReconcileApiOrdersOrderIdPaypalReconcilePost(body);
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


## paypalRestartApiOrdersOrderIdPaypalRestartPost

> any paypalRestartApiOrdersOrderIdPaypalRestartPost(orderId, authorization, xDemoRole)

Paypal Restart

### Example

```ts
import {
  Configuration,
  OrdersApi,
} from 'payfound-sdk';
import type { PaypalRestartApiOrdersOrderIdPaypalRestartPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new OrdersApi(config);

  const body = {
    // string
    orderId: orderId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies PaypalRestartApiOrdersOrderIdPaypalRestartPostRequest;

  try {
    const data = await api.paypalRestartApiOrdersOrderIdPaypalRestartPost(body);
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


## paypalResumeApiOrdersOrderIdPaypalResumePost

> any paypalResumeApiOrdersOrderIdPaypalResumePost(orderId, authorization, xDemoRole)

Paypal Resume

### Example

```ts
import {
  Configuration,
  OrdersApi,
} from 'payfound-sdk';
import type { PaypalResumeApiOrdersOrderIdPaypalResumePostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new OrdersApi(config);

  const body = {
    // string
    orderId: orderId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies PaypalResumeApiOrdersOrderIdPaypalResumePostRequest;

  try {
    const data = await api.paypalResumeApiOrdersOrderIdPaypalResumePost(body);
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


## refundApiOrdersOrderIdRefundPost

> any refundApiOrdersOrderIdRefundPost(orderId, authorization, xDemoRole)

Refund

### Example

```ts
import {
  Configuration,
  OrdersApi,
} from 'payfound-sdk';
import type { RefundApiOrdersOrderIdRefundPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new OrdersApi(config);

  const body = {
    // string
    orderId: orderId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies RefundApiOrdersOrderIdRefundPostRequest;

  try {
    const data = await api.refundApiOrdersOrderIdRefundPost(body);
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


## reserveApiOrdersReservePost

> any reserveApiOrdersReservePost(reserveInput, authorization, xDemoRole)

Reserve

### Example

```ts
import {
  Configuration,
  OrdersApi,
} from 'payfound-sdk';
import type { ReserveApiOrdersReservePostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new OrdersApi(config);

  const body = {
    // ReserveInput
    reserveInput: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies ReserveApiOrdersReservePostRequest;

  try {
    const data = await api.reserveApiOrdersReservePost(body);
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
| **reserveInput** | [ReserveInput](ReserveInput.md) |  | |
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

