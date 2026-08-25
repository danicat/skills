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
namegen.py — Legendary Comms Officers & Sci-Fi Agent Identity Generator
Generates iconic, memorable codenames for inter-session multi-agent mesh communication.
"""

import argparse
import random
import sys
from typing import Dict, List

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


def get_random_officer(include_uhura_boost: bool = True) -> Dict[str, str]:
    """Select a random communications officer profile."""
    if include_uhura_boost and random.random() < 0.25:
        return OFFICERS[0]
    return random.choice(OFFICERS)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate iconic sci-fi comms officer agent identities.")
    parser.add_argument("--id-only", action="store_true", help="Output only the slug identifier (e.g. nyota-uhura)")
    parser.add_argument("--all", action="store_true", help="List all available officers in the roster")
    args = parser.parse_args()

    if args.all:
        for off in OFFICERS:
            print(f"[{off['id']}] {off['name']} — {off['title']} ({off['ship']})")
            print(f"  Quote: \"{off['quote']}\"\n")
        return

    officer = get_random_officer()

    if args.id_only:
        print(officer["id"])
    else:
        print(f"✨ Designated Comms Officer: {officer['name']} ({officer['title']})")
        print(f"📡 Assigned Vessel / Hub: {officer['ship']}")
        print(f"💬 \"{officer['quote']}\"")
        print(f"🔑 Session ID: {officer['id']}")


if __name__ == "__main__":
    main()
