
# ProductInput


## Properties

Name | Type
------------ | -------------
`locationId` | string
`name` | string
`sku` | string
`description` | string
`category` | string
`priceCents` | number
`currency` | string
`quantity` | number
`gtin` | string
`brand` | string
`imageUrl` | string

## Example

```typescript
import type { ProductInput } from 'payfound-sdk'

// TODO: Update the object below with actual values
const example = {
  "locationId": null,
  "name": null,
  "sku": null,
  "description": null,
  "category": null,
  "priceCents": null,
  "currency": null,
  "quantity": null,
  "gtin": null,
  "brand": null,
  "imageUrl": null,
} satisfies ProductInput

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ProductInput
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


