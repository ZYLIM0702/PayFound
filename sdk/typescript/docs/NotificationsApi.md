# NotificationsApi

All URIs are relative to *http://127.0.0.1:8000*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**notificationsApiNotificationsGet**](NotificationsApi.md#notificationsapinotificationsget) | **GET** /api/notifications | Notifications |
| [**readNotificationApiNotificationsNotificationIdReadPost**](NotificationsApi.md#readnotificationapinotificationsnotificationidreadpost) | **POST** /api/notifications/{notification_id}/read | Read Notification |



## notificationsApiNotificationsGet

> any notificationsApiNotificationsGet(authorization, xDemoRole)

Notifications

### Example

```ts
import {
  Configuration,
  NotificationsApi,
} from 'payfound-sdk';
import type { NotificationsApiNotificationsGetRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new NotificationsApi(config);

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies NotificationsApiNotificationsGetRequest;

  try {
    const data = await api.notificationsApiNotificationsGet(body);
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


## readNotificationApiNotificationsNotificationIdReadPost

> any readNotificationApiNotificationsNotificationIdReadPost(notificationId, authorization, xDemoRole)

Read Notification

### Example

```ts
import {
  Configuration,
  NotificationsApi,
} from 'payfound-sdk';
import type { ReadNotificationApiNotificationsNotificationIdReadPostRequest } from 'payfound-sdk';

async function example() {
  console.log("🚀 Testing payfound-sdk SDK...");
  const config = new Configuration({ 
    // To configure API key authorization: demoRole
    apiKey: "YOUR API KEY",
    // Configure HTTP bearer authorization: bearerAuth
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new NotificationsApi(config);

  const body = {
    // string
    notificationId: notificationId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xDemoRole: xDemoRole_example,
  } satisfies ReadNotificationApiNotificationsNotificationIdReadPostRequest;

  try {
    const data = await api.readNotificationApiNotificationsNotificationIdReadPost(body);
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
| **notificationId** | `string` |  | [Defaults to `undefined`] |
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

