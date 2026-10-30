
# AppPosPluginRoutesConnectInput


## Properties

Name | Type
------------ | -------------
`merchantId` | string
`mode` | string
`name` | string
`baseUrl` | string
`token` | string
`authScheme` | string
`productsPath` | string
`branchesPath` | string
`healthPath` | string
`schedule` | string

## Example

```typescript
import type { AppPosPluginRoutesConnectInput } from 'payfound-sdk'

// TODO: Update the object below with actual values
const example = {
  "merchantId": null,
  "mode": null,
  "name": null,
  "baseUrl": null,
  "token": null,
  "authScheme": null,
  "productsPath": null,
  "branchesPath": null,
  "healthPath": null,
  "schedule": null,
} satisfies AppPosPluginRoutesConnectInput

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as AppPosPluginRoutesConnectInput
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


