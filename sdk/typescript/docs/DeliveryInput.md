
# DeliveryInput


## Properties

Name | Type
------------ | -------------
`providerId` | string
`address` | string
`notes` | string

## Example

```typescript
import type { DeliveryInput } from 'payfound-sdk'

// TODO: Update the object below with actual values
const example = {
  "providerId": null,
  "address": null,
  "notes": null,
} satisfies DeliveryInput

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as DeliveryInput
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


