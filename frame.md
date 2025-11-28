The conceptual structure of constructs.

# Project

```pt
{name}/
  data/
  docs/
  {packages}
  {envs}
  .gitignore
  README.md
```

# Package

```pt
{name}
  {name-or-src}/
    api/
    lib/
    config.{ext}
  tests/
  scripts/
  {envs}
  .gitignore
  README.md
```

# Dir

```plaintext
{dir}/
  {dirs}
  {files}
```

# File

```{lang}
{imports}

{constants}

{main}

{flows}
```

# Flow

```pt
{name}({params}) {return-type}
  {flows-and-steps}
```

- Name: {verb-noun}, {verb-noun-adj}, {verb-noun-prep-noun}

# Step

```pt
{variable} = {semantic-action}
```
