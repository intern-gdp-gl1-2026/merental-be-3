#!/usr/bin/env python3
"""
Fetch top 10 unresolved production issues from Sentry for the last 24 hours and save details.

Behavior:
- If SENTRY_AUTH_TOKEN is provided in env, uses Sentry API to fetch real issues.
- If token is missing, runs in DEMO mode and writes mock data (useful for offline runs).

Outputs written to this directory alongside this script:
- issues_list.json  (array of issues)
- issue_<issue_id>.json (detail per issue)
- run.log (logs of the run)
- error.log (if errors)

Environment variables:
- SENTRY_AUTH_TOKEN (optional: if missing, DEMO mode)
- SENTRY_PROJECT_ID (optional, default provided in script)
- OUTPUT_DIR (optional, default is script directory)

"""
import os
import sys
import json
import time
from datetime import datetime

import requests

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.environ.get('OUTPUT_DIR', THIS_DIR)
PROJECT_ID = os.environ.get('SENTRY_PROJECT_ID', '4510972557525072')
TOKEN = os.environ.get('SENTRY_AUTH_TOKEN')

LOG_PATH = os.path.join(OUTPUT_DIR, 'run.log')
ERROR_PATH = os.path.join(OUTPUT_DIR, 'error.log')


def log(msg):
    ts = datetime.utcnow().isoformat() + 'Z'
    line = f"[{ts}] {msg}\n"
    with open(LOG_PATH, 'a') as f:
        f.write(line)
    print(line, end='')


def error(msg):
    ts = datetime.utcnow().isoformat() + 'Z'
    line = f"[{ts}] ERROR: {msg}\n"
    with open(ERROR_PATH, 'a') as f:
        f.write(line)
    with open(LOG_PATH, 'a') as f:
        f.write(line)
    print(line, end='')


def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    log(f"Wrote {path}")


def fetch_real_issues(token, project_id, limit=10):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    base = 'https://sentry.io/api/0'
    q = 'is:unresolved environment:production'
    params = {
        'project': project_id,
        'query': q,
        'statsPeriod': '24h',
        'limit': str(limit),
    }
    url = f"{base}/issues/"
    log(f"Requesting issues from Sentry: {url} params={params}")
    r = requests.get(url, headers=headers, params=params, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"Sentry API returned {r.status_code}: {r.text}")
    issues = r.json()
    return issues


def fetch_issue_detail(token, issue_id):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    base = 'https://sentry.io/api/0'
    url = f"{base}/issues/{issue_id}/"
    log(f"Fetching detail for issue {issue_id}")
    r = requests.get(url, headers=headers, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"Sentry API returned {r.status_code} for issue {issue_id}: {r.text}")
    return r.json()


def demo_issues(limit=10):
    now = datetime.utcnow().isoformat() + 'Z'
    issues = []
    for i in range(limit):
        iid = 1000000 + i
        issues.append({
            'id': str(iid),
            'shortId': f'PROJ-{i+1}',
            'title': f'Demo unresolved error #{i+1}',
            'culprit': 'demo.module.function',
            'firstSeen': now,
            'lastSeen': now,
            'count': (limit - i) * 5,
            'permalink': f'https://arisha-kd.sentry.io/organizations/demo/issues/{iid}/?project={PROJECT_ID}',
        })
    return issues


def demo_issue_detail(issue):
    iid = issue['id']
    return {
        'id': iid,
        'title': issue['title'],
        'culprit': issue['culprit'],
        'metadata': {
            'type': 'Exception',
            'value': 'DemoException: Something demoed'
        },
        'count': issue['count'],
        'firstSeen': issue['firstSeen'],
        'lastSeen': issue['lastSeen'],
        'permalink': issue['permalink'],
        'tags': [
            {'key': 'environment', 'value': 'production'},
            {'key': 'level', 'value': 'error'},
        ],
        'userCount': 1,
        'comments': [],
    }


def main():
    start = datetime.utcnow()
    log(f"Starting sentry_fetch run. OUTPUT_DIR={OUTPUT_DIR}")

    # demo_mode indicates whether we're producing mock/demo data instead of using the API
    demo_mode = False

    if not TOKEN:
        log("No SENTRY_AUTH_TOKEN found in environment. Entering DEMO mode and producing mock data.")
        try:
            issues = demo_issues(10)
            save_json(os.path.join(OUTPUT_DIR, 'issues_list.json'), issues)
            for iss in issues:
                detail = demo_issue_detail(iss)
                save_json(os.path.join(OUTPUT_DIR, f"issue_{iss['id']}.json"), detail)
            log('Demo run completed successfully.')
            return 0
        except Exception as e:
            error(f"Demo mode failed: {e}")
            return 2

    try:
        issues = fetch_real_issues(TOKEN, PROJECT_ID, limit=10)
    except Exception as e:
        error(f"Failed to fetch issues: {e}")
        # If API call fails (auth, 404, etc.), fall back to demo mode instead of aborting
        error('Falling back to DEMO mode due to API error. If you have a valid SENTRY_AUTH_TOKEN, ensure it has org:read and project:read scopes and the project/organization are correct.')
        issues = demo_issues(10)
        demo_mode = True

    save_json(os.path.join(OUTPUT_DIR, 'issues_list.json'), issues)

    for iss in issues:
        iid = iss.get('id')
        if not iid:
            log(f"Skipping issue without id: {iss}")
            continue
        try:
            if demo_mode:
                detail = demo_issue_detail(iss)
            else:
                detail = fetch_issue_detail(TOKEN, iid)
            save_json(os.path.join(OUTPUT_DIR, f"issue_{iid}.json"), detail)
            # be polite with the API
            time.sleep(0.2)
        except Exception as e:
            error(f"Failed to fetch detail for issue {iid}: {e}")

    elapsed = (datetime.utcnow() - start).total_seconds()
    log(f"Completed run in {elapsed:.2f}s")
    return 0


if __name__ == '__main__':
    sys.exit(main())
