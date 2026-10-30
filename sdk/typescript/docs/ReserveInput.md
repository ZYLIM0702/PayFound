
# ReserveInput


## Properties

Name | Type
------------ | -------------
`productId` | string
`quantity` | number
`items` | [Array&lt;BasketItem&gt;](BasketItem.md)
`locationId` | string
`idempotencyKey` | string
`buyerName` | string

## Example

```typescript
import type { ReserveInput } from 'payfound-sdk'

// TODO: Update the object below with actual values
const example = {
  "productId": null,
  "quantity": null,
  "items": null,
  "locationId": null,
  "idempotencyKey": null,
  "buyerName": null,
} satisfies ReserveInput

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ReserveInput
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


