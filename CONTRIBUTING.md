# Contributing to zodify

## Setup

```sh
git clone https://github.com/junyoung2015/zodify.git
cd zodify
pip install -e ".[dev]"
```

## Running Tests

```sh
pytest
```

## Code Style

- No external formatter enforced yet — just be consistent with existing code
- Keep it simple: zodify is one file, zero dependencies. That's intentional.

## Submitting Changes

1. Fork the repo
2. Create a branch from `main`
3. Make your changes
4. Run `pytest` — all tests must pass
5. Open a PR with a summary of what and why
