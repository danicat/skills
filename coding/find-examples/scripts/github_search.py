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

import argparse
import json
import os
import sys
import requests
from datetime import datetime, timedelta

def search_github(dependency, languages, limit=5):
    """
    Searches GitHub for repositories using a specific dependency in target languages.
    Languages can be a comma-separated string or a list.
    """
    if isinstance(languages, str):
        languages = [l.strip() for l in languages.split(',')]

    manifest_files = {
        'go': 'go.mod',
        'typescript': 'package.json',
        'javascript': 'package.json',
        'python': 'requirements.txt',
        'rust': 'Cargo.toml',
        'java': 'pom.xml'
    }

    all_results = []
    repos = {}

    headers = {'Accept': 'application/vnd.github+json'}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers['Authorization'] = f"Bearer {token}"

    for lang in languages:
        filename = manifest_files.get(lang.lower())
        if not filename:
            query = f"{dependency} language:{lang}"
        else:
            query = f'"{dependency}" filename:{filename} language:{lang}'

        url = f"https://api.github.com/search/code?q={query}"

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            items = response.json().get('items', [])

            for item in items:
                repo_data = item['repository']
                repo_full_name = repo_data['full_name']
                if repo_full_name not in repos:
                    repos[repo_full_name] = {'repo': repo_data, 'lang': lang}
        except Exception as e:
            print(f"Error searching GitHub for {lang}: {e}", file=sys.stderr)

    # Enrich repo data
    enriched_repos = []
    for full_name, meta in list(repos.items())[:limit * 2]:
        try:
            repo_url = f"https://api.github.com/repos/{full_name}"
            repo_resp = requests.get(repo_url, headers=headers)
            repo_resp.raise_for_status()
            repo_info = repo_resp.json()

            enriched_repos.append({
                'full_name': repo_info['full_name'],
                'html_url': repo_info['html_url'],
                'description': repo_info['description'],
                'stars': repo_info['stargazers_count'],
                'updated_at': repo_info['updated_at'],
                'language': meta['lang'],
                'forks': repo_info['forks_count']
            })
        except Exception as e:
            continue

    enriched_repos.sort(key=lambda x: (x['stars'], x['updated_at']), reverse=True)
    return enriched_repos[:limit]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Find GitHub examples for a dependency.')
    parser.add_argument('dependency', help='The dependency string')
    parser.add_argument('--lang', default='go', help='Target languages (comma-separated, e.g. "go,typescript")')
    parser.add_argument('--limit', type=int, default=5, help='Limit results')

    args = parser.parse_args()
    results = search_github(args.dependency, args.lang, args.limit)


    if not results:
        print("No examples found.")
    else:
        print(json.dumps(results, indent=2))
