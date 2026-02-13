---
name: map-pdf-to-md
description: Convert PDF documents in chunks to an indexed set of Markdown formatted files.
argument-hint: [target path]
---

TARGET_PATH=$ARGUMENTS[0]
RESULT_DIR=stem($TARGET_PATH)/name($TARGET_PATH)/

N_MAX_CONCURRENT_FLOW=3
PAGE_GROUP_SIZE=10
FORMAT=categorize-pdf-format($TARGET_PATH)
assert(FORMAT in (deck, research))

```yaml:page-spec
n-image: {n_image}
n-text-block: {n_text_block}
```

```bash
split-pdf() {
    cpdf -split $TARGET_PATH -chunk $PAGE_GROUP_SIZE -o $RESULT_DIR/pdfs/%%%.pdf
}
```

```flow:main()
page_groups_pdfs ← split-pdf()
page_groups_mds ← dispatch-task-agent(() => map(page_groups_pdfs, map-page-group))
generate(
    $RESULT_DIR/index.md,
    index(page_groups_mds)
)
```

```flow:map-page-group(page_group)
page_group_md ← map(page_group, map-page)
generate(
    $RESULT_DIR/{first(page_group).number}-{last(page_group).number}.md,
    join(page_group_md, "\n\n---\n\n")
)
```

```flow:map-page(page)
image ← extract-page-as-image($page)
text ← ocr-extract-text($page)
generate(
````md:result-page-format
{hashes} {page.number}

{page-spec}

{content}
````,
    context=(image, text)
)
```

# Gotchas

- pdfs can be >10MB which exceeds YOUR CAPACITY.
  - If you attempt to read the whole pdf BEFORE SPLITTING, you may run out of memory.
  - Thus, split before reading. Ie, split without looking.
- Agents must dump their results directly to the $RESULT_DIR.
  - If they attempt to log their entire content back to the controller, you may exceed your context.
