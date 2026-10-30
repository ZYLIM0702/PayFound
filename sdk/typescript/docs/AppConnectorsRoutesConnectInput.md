
# AppConnectorsRoutesConnectInput


## Properties

Name | Type
------------ | -------------
`merchantId` | string
`provider` | string
`storeUrl` | string
`shopDomain` | string
`consumerKey` | string
`consumerSecret` | string

## Example

```typescript
import type { AppConnectorsRoutesConnectInput } from 'payfound-sdk'

// TODO: Update the object below with actual values
const example = {
  "merchantId": null,
  "provider": null,
  "storeUrl": null,
  "shopDomain": null,
  "consumerKey": null,
  "consumerSecret": null,
} satisfies AppConnectorsRoutesConnectInput

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as AppConnectorsRoutesConnectInput
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


