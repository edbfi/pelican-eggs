# Local validation

Repository CI, automated dependency updates and workflow-based deployment are disabled.
Validate changes locally and review dependency updates manually.
Use Conventional Commit titles and matching author sign-offs (`git commit -s`).

Available validation entry points (install the project toolchain first):

```sh
python3 .github/scripts/check-eggs.py
python3 .github/scripts/check-pair.py
```

See [CLAUDE.md](CLAUDE.md) for project-specific commands and test requirements.
