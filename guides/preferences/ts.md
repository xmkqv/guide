# TypeScript + SolidJS

- Assert invalid states; no defensive programming
- No `??` / `||` fallbacks; fail on missing

## Component

```typescript
type Props = {
  value: string;
  onAction(): void;
};

const CONSTANT = ...;

export default function ElementName(props: Props) {

  const api = useApi();

  const [store, setStore] = createStore({ ... });

  let inputRef: HTMLInputElement | undefined;

  const derived = createMemo(() => ...);

  const handleAction = () => ...;

  createEffect(() => ...);
  onMount(() => ...);
  onCleanup(() => ...);

  return <div>{props.value}</div>;
}
```

## Types

Prefer literal types, discriminated unions, mapped types, and template literals over loose records and primitives.

```typescript
// Discriminated unions over boolean flags
type Status =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "error"; message: string }
  | { kind: "ready"; data: Data };

// Exhaustive match
const assertNever = (x: never): never => {
  throw new Error(`Unhandled: ${x}`);
};

// Literal unions over string
type NodeType = "data" | "space";
type Permission = "r" | "rw";

// Template literals
type Route = `/${string}`;
type EventName = `on${Capitalize<string>}`;

// Mapped types
type Stores = { [K in NodeType]: Store<K> };

// as const for inference; satisfies for constraint
const ROUTES = {
  home: "/",
  user: "/user/:id",
} as const satisfies Record<string, Route>;
```

## Stores

```typescript
type Selected =
  | { kind: "none" }
  | { kind: "some"; id: string };

interface App {
  users: User[];
  selected: Selected;
}

const [store, setStore] = createStore<App>({
  users: [],
  selected: { kind: "none" },
});

// Derived
const active = createMemo(() => store.users.filter((u) => u.active));

// Path syntax
setStore("users", 0, "name", "Alice");

// Filter syntax
setStore("users", (u) => u.active, "notified", true);

// Multi-property mutation
setStore("users", 0, produce((user) => {
  user.name = "Bob";
  user.lastSeen = Date.now();
}));

// External data
setStore("users", reconcile(fetched));
```

## Reactivity

Store and props fields are exceptional in reactive contexts.

```typescript
// ✓ Reactive: access in JSX
<div>{store.user.name}</div>

// ✗ ANTIPATTERN: ugly
const name = () => store.user.name;
<div>{name()}</div>

// ✓ Reactive: direct access in effect
createEffect(() => {
  console.log(props.item.label);
});

// ✗ BROKEN: captured reference, not tracked
const item = props.item;
createEffect(() => {
  console.log(item.label);  // stale
});
```

## Validation

```typescript
import typia from "typia";

const user = typia.assert<User>(input);

if (typia.is<User>(input)) { ... }

const parsed = typia.assert<ApiResponse>(await res.json());

export const ok = <T>(v: T, msg = "not ok") => {
  if (v === null || v === undefined || v === false) throw new Error(msg);
  return v as NonNullable<T>;
};

const x = ok(maybeX, "x is required");
```

## Control Flow

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

# Lint Resolution

Escalation path for TypeScript/Biome issues:

1. **Fix the code** - Prefer proper typing over workarounds
2. **Run `bunx biome check --write .`** - Auto-fix formatting/import order
3. **If blocked by missing types** (eg generated schemas):
   ```typescript
   // biome-ignore lint/suspicious/noExplicitAny: awaiting type gen
   const { data } = await (db as any).from("table")
   ```

Inline exclusion format:
```
// biome-ignore {rule}: {reason <5 words}
```

Common reasons:
- `awaiting type gen`
- `test mock requires any`
- `external api shape`
- `legacy compatibility`

# Checks

- Omit section comments under 30 lines
