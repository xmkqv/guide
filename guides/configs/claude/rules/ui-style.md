---
paths:
  - "./**/*.{ts,tsx}"
---

Write declarative, robust, & self-explanatory Typescript
No comments

# Components

```tsx
const CONSTANT = ...;

type ControlType = "data" | "space";

interface Control {
  id: string;
  type: ControlType;
  label: string;
}

type Status =
  | { type: "idle" }
  | { type: "ready"; data: Data };

interface Props { // Prefer Interface for Public APIs
  value: string;
  onAction(): void; // Prefer Method Shorthand
};

const okSomething = typia.createAssert<Something>();

export default function Element(props: Props) { // Element prefered name; Simple, repeatable, default export

  const api = useApi();
  
  const [store, setStore] = createStore<ControlType>({ ... });

  const derived = createMemo(() => ...);

  const handleAction = () => ...;

  createEffect(() => ...);
  onMount(() => ...);
  onCleanup(() => ...);

  return (
    <div class="..." classList={{ "active": derived() }} onClick={handleAction}>
      {props.value}
    </div>
  );
}
```

Use SolidJS stores for state management.
Store and props fields are exceptional in reactive contexts.

```ts
interface Item { 
  id: string; 
  label: string 
};

const [items, setItems] = createStore<Item>([]);

const active = createMemo(() => store.users.filter((u) => u.active));

setStore("users", 0, "name", "Alice");

setStore("users", (u) => u.active, "notified", true);

setStore("users", 0, produce((user) => {
  user.name = "Bob";
  user.lastSeen = Date.now();
}));

setStore("users", reconcile(fetched));

<div>{store.user.name}</div>

createEffect(() => {
  console.log(props.item.label);
});
```

# SolidJS Control Flow

KISS with SolidJS control flow components.

```ts
<Show when={store.ready} fallback={<Loading />}>
  <Content />
</Show>

<For each={items()}>
  {(item) => <Item data={item} />}
</For>

<Switch>
  <Match when={store.status === "loading"}><Loading /></Match>
  <Match when={store.status === "error"}><Error /></Match>
</Switch>
```

# Types

Prefer literal types, discriminated unions, mapped types, and template literals
NEVER use `as` type assertions
NEVER use `!` non-null assertions
Prefer `satisfies` over `as` for constraining values
  `satisfies` validates without widening
  `as` silences without checking

Examples for assertion, constraint, and validation without widening:

```ts
const v = okType(v)
function lookup<K extends DataType>(...): DataMap[K] | undefined
const seeds = [{ ... }] satisfies Seed[]
```

# Exports

Export iff referenced across module boundaries
