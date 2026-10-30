
# Msg


## Properties

Name | Type
------------ | -------------
`id` | string
`role` | string
`content` | any
`images` | Array&lt;{ [key: string]: any; } | null&gt;

## Example

```typescript
import type { Msg } from 'payfound-sdk'

// TODO: Update the object below with actual values
const example = {
  "id": null,
  "role": null,
  "content": null,
  "images": null,
} satisfies Msg

console.log(example)

// Convert the instance to a JSON string
const exampleJSON: string = JSON.stringify(example)
console.log(exampleJSON)

// Parse the JSON string back to an object
const exampleParsed = JSON.parse(exampleJSON) as Msg
console.log(exampleParsed)
```

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


