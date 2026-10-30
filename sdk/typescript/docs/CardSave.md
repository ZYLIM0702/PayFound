
# CardSave


## Properties

Name | Type
------------ | -------------
`merchantId` | string
`name` | string
`kind` | string
`days` | number
`focus` | string

## Example

```typescript
import type { CardSave } from 'payfound-sdk'

// TODO: Update the object below with actual values
const example = {
  "merchantId": null,
  "name": null,
  "kind": null,
  "days": null,
  "focus": null,
} satisfies CardSave

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as CardSave
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


