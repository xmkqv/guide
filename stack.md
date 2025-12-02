
# Style

[Style System](style/README.md)

```bash
claude: /guide:gen-moodboard... [mood] [jumble] → (triggers just style-align)
/guide:gen-art [mood] [name] [jumble]
```

## Diagrams

```bash
just agent gen-diagram "generate a diagram based on README.md in /Users/m/guide"
```

# Configuration

Config paths in ~/.zshrc

## Markdown

Lint: [markdownlint](configs/.markdownlint.json); Auto.

## Typescript

Format: [Biome](configs/biome.json); Auto (requires ~/biome.json symlink maintenance).

## Python

Type Check: [Pyright](configs/pyrightconfig.json); Requires symlink.

```bash
ln -s ~/guide/configs/{name} pyrightconfig.json
```

Format & Lint: [Ruff](configs/ruff.toml); Auto.

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
