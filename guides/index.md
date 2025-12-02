
# Commands

- gen-art
- gen-mood
- gen-mission

# Configs

```sh
# ~/.zshrc
MARKDOWNLINT_CONFIG="$GUIDES_DIR/configs/.markdownlint.json"
RUFF_CONFIG="$GUIDES_DIR/configs/ruff.toml"

# ./vscode/settings.json; nb resolve variables
...
"markdownlint.config": "${GUIDES_DIR}/configs/.markdownlint.json"
...
"biome.configurationPath": "${GUIDES_DIR}/configs/biome.json",
```

```bash
ln -s "$GUIDES_DIR/configs/vscode/settings.json" {vscode_user_settings_path}
ln -s "$GUIDES_DIR/configs/claude/settings.json" ~/.claude/settings.json
ln -s "$GUIDES_DIR/configs/pyrightconfig.json"
ln -s "$GUIDES_DIR/configs/biome.json" ~/biome.json
```

# Preferences

- code.md
- meta.md
- ml.md
- prose.md
- python.md

# Scripts

- cleanup-mac.sh

# Styles

- cv (A4, portrait)
- doc (A4, portrait)
- deck (16:9, landscape)

## Moods

- spec.schema.yaml
- mood.schema.yaml

---

HOW TO

---

# Environment

Environment Variables: direnv

```bash
direnv allow
```

```pt
.env
.env.{development|dev}
.env.{production|prod}
```

# Entrypoint

- justfile
