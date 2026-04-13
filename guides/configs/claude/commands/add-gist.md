---
title: Gist Preview
task: Create public GitHub gist with preview link for HTML files
allowed-tools: Bash(gh gist:*)
disable-model-invocation: true
---

# Create Gist with Preview Link

The user wants to create a public GitHub gist and get a preview link for HTML files.

## Your Task

1. Create the gist using GitHub CLI:

   ```bash
   gh gist create $ARGUMENTS --public --desc "Preview via gist.githack.com"
   ```

2. Extract the gist ID and username from the output URL

3. Generate the preview URL:

   ```
   https://gist.githack.com/[user]/[id]/raw/[filename]
   ```

4. Return the preview link to the user

---

## Reference: About This Command

Creates public GitHub gists and generates preview links that render HTML files properly without GitHub's interface framing.
