# Special Agent System

agent name task workdir=".":
    #!/usr/bin/env bash
    set -e
    workdir="$(realpath "{{ workdir }}")"
    cd "specials/{{ name }}" || { ls -1 specials/; exit 1; }
    mcp_args=$([ -f .mcp.json ] && echo "--mcp-config .mcp.json" || echo "")
    exec claude $mcp_args --add-dir "$workdir" --verbose -p "use {{ name }}: {{ task }}"

