
# Commands

- gen-art
- gen-mood
- gen-mission

# Configs

```sh
# ~/.zshrc
MARKDOWNLINT_CONFIG="$GUIDES_DIR/configs/.markdownlint.json"

# ./vscode/settings.json; nb resolve variables
...
"markdownlint.config": "${GUIDES_DIR}/configs/.markdownlint.json",

# configs/claude/settings.json
...
 "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "/Users/m/qxotk/libs/guide/qxgo/qxgo"
          }
        ]
      }
    ]
  },
  ...
```

```bash
ln -s "$GUIDES_DIR/configs/vscode/settings.json" {vscode_user_settings_path}
ln -s "$GUIDES_DIR/configs/claude/settings.json" ~/.claude/settings.json
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

# Styles

- cv (A4, portrait)
- doc (A4, portrait)
- deck (16:9, landscape)

## Moods

- spec.schema.yaml
- mood.schema.yaml
