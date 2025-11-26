# Contributing to Session Guard

Thanks for your interest in contributing to **Session Guard**! 🎉
This project aims to be a world‑class, production‑ready Django package for device‑aware session management.

## 1. Ways to contribute

- Report bugs or edge cases.
- Improve docs, examples and demo UI.
- Implement new features (device verification, OIDC/mobile support, JWT revocation, etc.).
- Improve tests, CI, observability and performance.

Before starting a larger change, consider opening a GitHub issue or discussion to align on scope and design.

## 2. Code of conduct

Please be respectful, constructive and inclusive. Treat other contributors the way you'd like to be treated.
Harassment, personal attacks or discriminatory behaviour are not welcome.

## 3. Local development setup

### 3.1. Fork & clone

```bash
git clone https://github.com/herchila/session-guard.git
cd session-guard
```

### 3.2. Install dependencies (Poetry)

If you don't have Poetry:

```bash
pip install poetry
```

Then install project dependencies:

```bash
poetry install
```

This will install:

- Django (for the demo + tests)
- pytest / pytest‑django
- black, ruff, mypy, django‑stubs
- pre‑commit

### 3.3. Running tests

```bash
poetry run pytest
```

To run only a subset of tests:

```bash
poetry run pytest tests/test_middleware.py
```

### 3.4. Running the demo

The repo ships a minimal demo project under `demo/`:

```bash
poetry run python demo/manage.py migrate
poetry run python demo/manage.py createsuperuser
poetry run python demo/manage.py runserver
```

Then open `http://127.0.0.1:8000/account/sessions/` after logging in to see the “Your sessions” page.

## 4. Code style & quality checks

We use **black**, **ruff**, **mypy** and **pytest**.
All of them can be run via **pre‑commit** or individually:

```bash
poetry run black .
poetry run ruff check .
poetry run mypy .
poetry run pytest
```

To set up pre‑commit:

```bash
poetry run pre-commit install
poetry run pre-commit run --all-files
```

Please make sure all checks pass before opening a PR.

## 5. Git workflow & pull requests

- Use the standard GitHub Flow:
  - Fork the repo.
  - Create a branch from `master`, e.g. `feat/device-verification` or `fix/middleware-edge-case`.
- Keep PRs focused and small when possible.
- Add or update tests that cover your changes.
- Update documentation (README, examples, changelog) when appropriate.
- In the PR description, explain:
  - What you changed.
  - Why it's needed.
  - How you tested it (manual + automated).

## 6. Versioning

Session Guard follows **Semantic Versioning (SemVer)**:

- `MAJOR.MINOR.PATCH`
- Breaking changes will bump the major version.
- New features in a backwards‑compatible way bump the minor version.
- Bug fixes bump the patch version.

Changes should be reflected in `CHANGELOG.md`.

## 7. Questions?

If you're unsure how to implement something or where a feature belongs, open an issue or discussion on GitHub.
We want this to be a welcoming project for both new and experienced contributors.
