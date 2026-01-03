# Code style with pre-commit

Use the shared pre-commit config at `src/agent/.pre-commit-config.yaml` to keep
formatting and linting consistent.

## One-time setup
- Install pre-commit: `pip install pre-commit`
- Install the hooks: `pre-commit install -c src/agent/.pre-commit-config.yaml`

## Running checks
- Run on all files: `pre-commit run --all-files -c src/agent/.pre-commit-config.yaml`
- Run on staged files (default): `pre-commit run -c src/agent/.pre-commit-config.yaml`

## What the hooks do
- black: format Python code with Python 3.11 settings
- flake8 (with flake8-bugbear): lint Python
- isort: sort and group imports


## Code examples

### Clean imports (isort + black)
```python
from __future__ import annotations

from dataclasses import dataclass

from httpx import Client


@dataclass
class User:
	id: str
	name: str


def fetch_user(
    client: Client,
    user_id: str
) -> User:
	resp = client.get(f"/users/{user_id}")
	resp.raise_for_status()
	payload = resp.json()
	return User(id=payload["id"], name=payload["name"])
```

### Respect line length (flake8 E501)
```python
def format_profile(name: str, role: str) -> str:
	# Keep f-strings concise to stay under 79 chars
	return f"{name} — {role}"
```
