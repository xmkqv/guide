Complete Configuration.

Config env paths in ~/.zshrc

# Markdown

Lint: [markdownlint](configs/.markdownlint.json); Auto.

# Typescript

Format: [Biome](configs/biome.json); Auto (requires ~/biome.json symlink maintenance).

# Python

Type Check: [Pyright](configs/pyrightconfig.json); Requires symlink.

```bash
ln -s ~/guide/configs/{name} pyrightconfig.json
```

Format & Lint: [Ruff](configs/ruff.toml); Auto.

# Env

Environment Variables: direnv

```bash
direnv allow
```

```pt
.env
.env.{development|dev}
.env.{production|prod}
```
