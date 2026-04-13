---
description: TypeScript and SolidJS Style Guide
paths:
  - "**/*.{ts,tsx}"
---

Declarative, robust, self-explanatory TypeScript.

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

interface Props {
  value: string;
  onAction(): void;  // method shorthand
};

const okSomething = typia.createAssert<Something>();

export default function (props: Props) {
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

# Components

- unnamed default export; no component name
- interface > type for public APIs
- method shorthand in interfaces

order: hooks → stores → derived → handlers → effects → lifecycle → JSX

# Stores

SolidJS stores for state management.
Store + props fields reactive in reactive contexts.

```ts
const [items, setItems] = createStore<Item>([]);
const active = createMemo(() => store.users.filter((u) => u.active));
setStore("users", 0, "name", "Alice");
setStore("users", (u) => u.active, "notified", true);
setStore("users", 0, produce((user) => {
  user.name = "Bob";
  user.lastSeen = Date.now();
}));
setStore("users", reconcile(fetched));
```

```ts
const newTypeStore = <I, V>(init: (i: I) => V) => {
  const [store, setStore] = createStore<V[]>([])
  return mergeProps(store, {
    add(i: I) { ... },
    get(predicate: (o: V) => boolean): V { ... },
    setKey<K extends keyof V>(k: K, vk: V[K], ...ids: string[]) { ... },
    deln(...ids: string[]) { ... },
  })
}
type Store<I, V> = ReturnType<typeof newTypeStore<I, V>>
```

# Control Flow

```tsx
<Show when={store.ready} fallback={<Loading />}>
  <Content />
</Show>

<Show when={signal()} keyed>
  {(v) => <SomethingCool {...v} />}
</Show>

<For each={items}>
  {(v) => <Item data={v} />}
</For>

<Switch>
  <Match when={store.status === "loading"}><Loading /></Match>
  <Match when={store.status === "error"}><Error /></Match>
</Switch>
```

# Types

- literal types, discriminated unions, mapped types, template literals
- `satisfies` > `as` (validates without widening)
- `type-fest` for deep transforms, intersection flattening, config merging
  common: `PartialDeep`, `ReadonlyDeep`, `Merge`, `Simplify`, `SetRequired`, `SetOptional`, `Tagged`

```ts
const v = okType(v)
function lookup<K extends DataType>(...): DataMap[K] | undefined
const seeds = [{ ... }] satisfies Seed[]
```

# Style

- guard clauses + early returns > try/catch, switch/break, nested ifs
- happy path falls through flat
- repeated setup/teardown → push lifecycle into callee as optional param
- shared switch body + ternary for variation; early-return outlier

# Exports

export iff referenced across module boundaries

invs:
  ¬ `as` type assertions
  ¬ `!` non-null assertions
  ¬ npm (use bun)
  constants + config → `src/config.ts`
