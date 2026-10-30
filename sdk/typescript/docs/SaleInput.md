
# SaleInput


## Properties

Name | Type
------------ | -------------
`items` | [Array&lt;Line&gt;](Line.md)
`discountKind` | string
`discountValue` | number
`paymentMethod` | string
`outcome` | string
`idempotencyKey` | string

## Example

```typescript
import type { SaleInput } from 'payfound-sdk'

// TODO: Update the object below with actual values
const example = {
  "items": null,
  "discountKind": null,
  "discountValue": null,
  "paymentMethod": null,
  "outcome": null,
  "idempotencyKey": null,
} satisfies SaleInput

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as SaleInput
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


