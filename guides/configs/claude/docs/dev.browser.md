# Browser Automation

Playwright MCP via [fast-playwright-mcp](https://github.com/tontoko/fast-playwright-mcp).

## Modes

| Mode     | Tokens  | Use Case                  |
|----------|---------|---------------------------|
| Snapshot | 500-4k  | Forms, navigation, data   |
| Vision   | 10-15k  | Layout, visual QA, design |
| Batch    | -90%    | Multi-step workflows      |

Default: Snapshot (accessibility tree). Heavy pages: 20-50k tokens.

## Selectors

Priority: ref > role > css > text. Fallback automatic.

## Token Optimization

| Strategy      | Savings | How                                    |
|---------------|---------|----------------------------------------|
| Skip snapshot | 70-80%  | `includeSnapshot: false`               |
| Diff tracking | 80%     | `diffOptions: { enabled: true }`       |
| Scope limit   | 50%     | `snapshotOptions: { selector: "#id" }` |
| Batch         | 90%     | `browser_batch_execute`                |

## Workflow

1. Navigate → full snapshot
2. Interact → skip snapshot (batch)
3. Verify → snapshot or screenshot

## Error Recovery

| Error             | Recovery                        |
|-------------------|---------------------------------|
| Element not found | Alternate selector; Vision mode |
| Timeout           | Increase timeout; check load    |
| Stale element     | Re-snapshot; fresh ref          |
| Dialog blocking   | `browser_handle_dialog` first   |

Loop detection: Stop after 3x same call or 2x no state change.
