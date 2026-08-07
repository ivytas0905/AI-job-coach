import { createIntentKey } from "./idempotency";

it("keeps one key stable for an intent and creates a new key for a new intent", () => {
  let sequence = 0;
  const make = () => `intent-${++sequence}`;
  const first = createIntentKey(make);
  expect(first.value).toBe(first.value);
  expect(createIntentKey(make).value).not.toBe(first.value);
  expect(Object.isFrozen(first)).toBe(true);
});

