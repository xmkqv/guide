# Paths

## Globals

```text
GUIDES  = $GUIDES
STYLE   = $GUIDES/style
COMMS   = $STYLE/comms
MOODS   = $STYLE/moods
```

## Locals

```text
RESULTS_ = $CWD/results
STYLE_   = $RESULTS_/style
LIMN_    = $RESULTS_/limn
```

# Commands

## gen-mood

```text
mood(name, n, brief) :=
  images ← search(brief) |> select(n)
  specs  ← images.map(img → extract(img, $STYLE/spec.schema.yaml))
  brief  ← compose(specs)
  style  ← embody(brief)
  → $STYLE_/{name}/   (working directory)
  → $MOODS/{name}.css (exported style)
```

## gen-comm

```text
comm(mood, format, brief) :=
  check exists $MOODS/{mood}.css, $COMMS/{format}.css
  html ← compose(brief, $MOODS/{mood}.css, $COMMS/{format}.css)
  pdf  ← render(html)
  → $RESULTS_/{gen-reasonable-name()}.html
  → $RESULTS_/{gen-reasonable-name()}.pdf
```

## gen-limn

```text
limn(path) :=
  system ← read(path/**)
  model  ← extract(system, likec4.schema)
  views  ← model.map(scope → diagram(scope))
  → $LIMN_/model.c4
  → $LIMN_/*.png
```

# Configs

```sh
# ~/.zshrc
MARKDOWNLINT_CONFIG="$GUIDES/configs/.markdownlint.json"
```

```bash
ln -s "$GUIDES/configs/vscode/settings.json" {vscode_user_settings_path}
ln -s "$GUIDES/configs/claude/settings.json" ~/.claude/settings.json
```

# Preferences

- code.md
- meta.md
- ml.md
- prose.md
- py.md
- ts.md

# Scripts

- cleanup-mac.sh

# Style

- spec.schema.yaml

## Comms

- cv.css (letter, portrait, tight)
- doc.css (letter, portrait)
- deck.css (1920×1080, landscape)
- poster.css (1080×1920, portrait)

## Moods

Exported mood CSS files live here.
