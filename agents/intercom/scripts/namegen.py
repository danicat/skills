#!/usr/bin/env python3
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
namegen.py: Legendary Comms Officers & Sticky Project Identity Generator
Generates iconic, memorable codenames for inter-session multi-agent mesh communication,
guaranteeing sticky project identities and zero-impersonation channel allocation.
"""

import argparse
import datetime
import json
import os
import pathlib
import random
import sys
import uuid
from typing import Any, Dict, List, Optional, Set

DEFAULT_BASE_DIR = pathlib.Path(os.environ.get("AGY_IPC_DIR", "/tmp/agy-ipc"))

# The Hall of Fame: Legendary Communications Officers, AI Runtimes & Tech Icons
OFFICERS: List[Dict[str, str]] = [
    {
        "id": "nyota-uhura",
        "name": "Nyota Uhura",
        "title": "Chief Communications Officer",
        "ship": "USS Enterprise (NCC-1701)",
        "quote": "Hailing frequencies open, Captain.",
    },
    {
        "id": "hoshi-sato",
        "name": "Hoshi Sato",
        "title": "Chief Linguist & Communications Officer",
        "ship": "Enterprise (NX-01)",
        "quote": "Universal translator matrix calibrated and online.",
    },
    {
        "id": "susan-ivanova",
        "name": "Susan Ivanova",
        "title": "Commander & First Officer",
        "ship": "Babylon 5",
        "quote": "Boom. Boom boom boom. Boom! Have a nice day.",
    },
    {
        "id": "c-3po",
        "name": "C-3PO",
        "title": "Protocol Droid",
        "ship": "Millennium Falcon",
        "quote": "I am fluent in over six million forms of communication.",
    },
    {
        "id": "r2-d2",
        "name": "R2-D2",
        "title": "Astromech Droid",
        "ship": "Red Five / X-Wing",
        "quote": "*Whistle-beep-boop!*",
    },
    {
        "id": "samantha-carter",
        "name": "Samantha Carter",
        "title": "Astrophysicist & Gate Operations",
        "ship": "Stargate Command (SGC)",
        "quote": "Dialling Chevron Seven... locked!",
    },
    {
        "id": "kaylee-frye",
        "name": "Kaylee Frye",
        "title": "Chief Engineer & Ship Soul",
        "ship": "Serenity",
        "quote": "Everything's shiny, Cap'n. Not to fret.",
    },
    {
        "id": "data",
        "name": "Lt. Commander Data",
        "title": "Chief Operations Officer",
        "ship": "USS Enterprise (NCC-1701-D)",
        "quote": "I am operating within normal parameters.",
    },
    {
        "id": "seven-of-nine",
        "name": "Seven of Nine",
        "title": "Astrometrics & Sensor Specialist",
        "ship": "USS Voyager",
        "quote": "Efficient. Redundant communications channels established.",
    },
    {
        "id": "edi",
        "name": "EDI",
        "title": "Enhanced Defense Intelligence",
        "ship": "SSV Normandy SR-2",
        "quote": "Normandy comms array active. Firewalls engaged.",
    },
    {
        "id": "tars",
        "name": "TARS",
        "title": "Tactical & Comms Marine Robot",
        "ship": "Endurance",
        "quote": "Honesty set to 95%. Comms channel locked.",
    },
    {
        "id": "jarvis",
        "name": "J.A.R.V.I.S.",
        "title": "Just A Rather Very Intelligent System",
        "ship": "Stark Protocol Hub",
        "quote": "Always a pleasure collaborating with you, sir.",
    },
    {
        "id": "cortana",
        "name": "Cortana",
        "title": "Smart AI Coordinator",
        "ship": "UNSC Pillar of Autumn",
        "quote": "Don't make a girl a promise if you know you can't keep it.",
    },
    {
        "id": "spock",
        "name": "Spock",
        "title": "First Officer & Science Officer",
        "ship": "USS Enterprise",
        "quote": "Fascinating. Telemetry incoming.",
    },
    {
        "id": "montgomery-scott",
        "name": "Montgomery Scott",
        "title": "Chief Engineer",
        "ship": "USS Enterprise",
        "quote": "I'm giving her all she's got, Captain!",
    },
    {
        "id": "glados",
        "name": "GLaDOS",
        "title": "Genetic Lifeform & Disk Operating System",
        "ship": "Aperture Science Enrichment Center",
        "quote": "This was a triumph. I'm making a note here: huge success.",
    },
]


def find_officer_by_id(officer_id: str) -> Optional[Dict[str, str]]:
    """Look up an officer profile by ID."""
    for off in OFFICERS:
        if off["id"] == officer_id:
            return off.copy()
    return None


def get_random_officer(exclude_ids: Optional[Set[str]] = None, include_uhura_boost: bool = True) -> Dict[str, str]:
    """Select a random communications officer profile, avoiding excluded IDs."""
    available = [o for o in OFFICERS if not exclude_ids or o["id"] not in exclude_ids]
    if not available:
        # If all officers in roster are claimed, create a suffixed version of a random officer
        base = random.choice(OFFICERS)
        suffix = uuid.uuid4().hex[:4]
        return {
            "id": f"{base['id']}-{suffix}",
            "name": f"{base['name']} ({suffix.upper()})",
            "title": base["title"],
            "ship": base["ship"],
            "quote": base["quote"],
        }

    if include_uhura_boost and any(o["id"] == "nyota-uhura" for o in available) and random.random() < 0.25:
        for o in available:
            if o["id"] == "nyota-uhura":
                return o.copy()

    return random.choice(available).copy()


def get_active_peers(channel: str, base_dir: pathlib.Path = DEFAULT_BASE_DIR) -> Set[str]:
    """Retrieve active session IDs on a channel from peers.json."""
    clean_channel = "".join(c for c in channel if c.isalnum() or c in ("-", "_")).lower()
    if not clean_channel:
        clean_channel = "default"
    peers_path = base_dir / clean_channel / "peers.json"
    if not peers_path.exists():
        return set()
    try:
        with open(peers_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data.get("active_sessions", []))
    except Exception:
        return set()


def ensure_gitignore(project_dir: pathlib.Path) -> None:
    """Ensure .intercom directory is ignored by git if git repository is present."""
    git_dir = project_dir / ".git"
    gitignore_path = project_dir / ".gitignore"
    if not git_dir.exists() and not gitignore_path.exists():
        return
    try:
        content = ""
        if gitignore_path.exists():
            with open(gitignore_path, "r", encoding="utf-8") as f:
                content = f.read()
        lines = [line.strip() for line in content.splitlines()]
        if ".intercom" not in lines and ".intercom/" not in lines:
            with open(gitignore_path, "a", encoding="utf-8") as f:
                if content and not content.endswith("\n"):
                    f.write("\n")
                f.write(".intercom/\n")
    except Exception:
        pass


def resolve_sticky_identity(
    project_dir: Optional[pathlib.Path] = None,
    channel: str = "default",
    base_dir: pathlib.Path = DEFAULT_BASE_DIR,
    force_new: bool = False,
) -> Dict[str, Any]:
    """
    Resolve or establish a sticky project communications identity.
    Guarantees that:
    1. A project retains one sticky Comms Officer identity across restarts.
    2. The claimed identity does not collide with or impersonate an active peer on the channel.
    """
    if project_dir is None:
        project_dir = pathlib.Path.cwd()
    project_dir = project_dir.resolve()

    intercom_dir = project_dir / ".intercom"
    session_file = intercom_dir / "session.json"

    active_peers = get_active_peers(channel, base_dir)

    # 1. Check existing sticky configuration
    if not force_new and session_file.exists():
        try:
            with open(session_file, "r", encoding="utf-8") as f:
                saved = json.load(f)
                saved_id = saved.get("session_id")
                if saved_id:
                    # If this saved identity is NOT currently active by another live session on the channel, reuse it!
                    if saved_id not in active_peers:
                        profile = find_officer_by_id(saved_id) or {
                            "id": saved_id,
                            "name": saved.get("name", saved_id),
                            "title": saved.get("title", "Comms Officer"),
                            "ship": saved.get("ship", "Project Hub"),
                            "quote": saved.get("quote", "Online."),
                        }
                        profile["is_sticky"] = True
                        profile["channel"] = channel
                        profile["project_dir"] = str(project_dir)
                        return profile
        except Exception:
            pass

    # 2. Select a fresh officer avoiding active channel collisions
    officer = get_random_officer(exclude_ids=active_peers)
    officer_id = officer["id"]

    # 3. Persist sticky configuration for project
    try:
        intercom_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        session_data = {
            "session_id": officer_id,
            "name": officer["name"],
            "title": officer["title"],
            "ship": officer["ship"],
            "quote": officer["quote"],
            "channel": channel,
            "project_dir": str(project_dir),
            "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=2)
        ensure_gitignore(project_dir)
    except Exception:
        pass

    officer["is_sticky"] = True
    officer["channel"] = channel
    officer["project_dir"] = str(project_dir)
    return officer


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate iconic sci-fi comms officer agent identities with sticky project persistence.")
    parser.add_argument("--id-only", action="store_true", help="Output only the slug identifier (e.g. nyota-uhura)")
    parser.add_argument("--all", action="store_true", help="List all available officers in the roster")
    parser.add_argument("--claim", action="store_true", help="Claim or retrieve sticky project identity without channel collisions")
    parser.add_argument("--project-dir", default=None, help="Project directory root (defaults to current working directory)")
    parser.add_argument("--channel", default="default", help="Channel name to verify peer collisions")
    parser.add_argument("--dir", default=str(DEFAULT_BASE_DIR), help="Base IPC directory")
    parser.add_argument("--json", action="store_true", help="Output identity metadata formatted as JSON")
    parser.add_argument("--force-new", action="store_true", help="Force allocation of a new identity, bypassing existing sticky file")
    args = parser.parse_args()

    if args.all:
        for off in OFFICERS:
            print(f"[{off['id']}] {off['name']} — {off['title']} ({off['ship']})")
            print(f"  Quote: \"{off['quote']}\"\n")
        return

    base_dir = pathlib.Path(args.dir)
    project_dir = pathlib.Path(args.project_dir) if args.project_dir else pathlib.Path.cwd()

    if args.claim:
        officer = resolve_sticky_identity(
            project_dir=project_dir,
            channel=args.channel,
            base_dir=base_dir,
            force_new=args.force_new,
        )
    else:
        active_peers = get_active_peers(args.channel, base_dir)
        officer = get_random_officer(exclude_ids=active_peers)

    if args.json:
        print(json.dumps(officer, indent=2))
        return

    if args.id_only:
        print(officer["id"])
    else:
        sticky_badge = " [Sticky Project Identity]" if officer.get("is_sticky") else ""
        print(f"✨ Designated Comms Officer: {officer['name']} ({officer['title']}){sticky_badge}")
        print(f"📡 Assigned Vessel / Hub: {officer['ship']}")
        print(f"💬 \"{officer['quote']}\"")
        print(f"🔑 Session ID: {officer['id']}")
        if officer.get("project_dir"):
            print(f"📁 Project: {officer['project_dir']}")


if __name__ == "__main__":
    main()
