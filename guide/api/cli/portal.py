"""Password-protected Netlify portals."""

import json
import subprocess
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Any

import tyro
from rich import print

SITE_PREFIX = "qx-"
Site = dict[str, Any]


def _netlify(args: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["netlify", *args], capture_output=capture, text=True, check=True)


def _sites() -> list[Site]:
    return json.loads(_netlify(["sites:list", "--json"], capture=True).stdout)


def _password_settings_url(site_name: str) -> str:
    return f"https://app.netlify.com/sites/{site_name}/configuration/general#visitor-access"


@dataclass(frozen=True)
class _Add:
    """Deploy directory to Netlify."""

    name: Annotated[str, tyro.conf.Positional]
    html: Annotated[Path, tyro.conf.Positional]
    with_password: Annotated[bool, tyro.conf.arg(name="with-password")] = False
    """Open browser to set password after deploy."""


@dataclass(frozen=True)
class _Ls:
    """List all portal deployments."""


@dataclass(frozen=True)
class _Rm:
    """Remove a portal deployment."""

    name: Annotated[str, tyro.conf.Positional]


@dataclass(frozen=True)
class _Set:
    """Update existing portal with new content."""

    name: Annotated[str, tyro.conf.Positional]
    html: Annotated[Path, tyro.conf.Positional]


@dataclass(frozen=True)
class Portal:
    """Manage password-protected Netlify portals."""

    cmd: (
        Annotated[_Add, tyro.conf.subcommand("add", prefix_name=False)]
        | Annotated[_Ls, tyro.conf.subcommand("ls", prefix_name=False)]
        | Annotated[_Rm, tyro.conf.subcommand("rm", prefix_name=False)]
        | Annotated[_Set, tyro.conf.subcommand("set", prefix_name=False)]
    )


def run(cmd: Portal) -> int:
    match cmd.cmd:
        case _Add(name=name, html=html, with_password=with_password):
            site_name = f"{SITE_PREFIX}{name}"

            _netlify(["sites:create", "--name", site_name, "--disable-linking", "--account-slug", "qxotk"], capture=True)
            site_id = next(s["id"] for s in _sites() if s["name"] == site_name)
            _netlify(["deploy", "--dir", str(html), "--prod", "--site", site_id])

            print(f"URL: https://{site_name}.netlify.app")

            if with_password:
                webbrowser.open(_password_settings_url(site_name))

        case _Ls():
            for site in _sites():
                if site["name"].startswith(SITE_PREFIX):
                    print(f"{site['name']}\t{site['ssl_url']}")

        case _Rm(name=name):
            site_name = f"{SITE_PREFIX}{name}"
            site = next((s for s in _sites() if s["name"] == site_name), None)
            if not site:
                print(f"Portal not found: {name}")
                return 1
            _netlify(["sites:delete", site["id"], "-f"])
            print(f"Removed: {name}")

        case _Set(name=name, html=html):
            site_name = f"{SITE_PREFIX}{name}"
            site = next((s for s in _sites() if s["name"] == site_name), None)
            if not site:
                print(f"Portal not found: {name}")
                return 1
            _netlify(["deploy", "--dir", str(html), "--prod", "--site", site["id"]])
            print(f"URL: {site['ssl_url']}")

    return 0
