export interface IntentKey { readonly value: string }

export function createIntentKey(randomUUID: () => string = crypto.randomUUID.bind(crypto)): IntentKey {
  return Object.freeze({ value: randomUUID() });
}

