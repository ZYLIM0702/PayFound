
# ProfileInput


## Properties

Name | Type
------------ | -------------
`displayName` | string
`addresses` | [Array&lt;AddressInput&gt;](AddressInput.md)
`notifications` | { [key: string]: boolean; }

## Example

```typescript
import type { ProfileInput } from 'payfound-sdk'

// TODO: Update the object below with actual values
const example = {
  "displayName": null,
  "addresses": null,
  "notifications": null,
} satisfies ProfileInput

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as ProfileInput
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


