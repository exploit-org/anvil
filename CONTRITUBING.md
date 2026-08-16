# Contributing

Thanks for contributing to Anvil.

## Where to post what

- **Security issues:** do **NOT** open a public issue or discussion. See [SECURITY](SECURITY.md) and email us at `security@exploit.org`.
- **Questions / support:** use **GitHub Discussions** (Q&A).
- **Bugs / actionable work:** use **GitHub Issues** (only after you can describe a reproducible problem).
- **Design proposals / larger changes:** start in **Discussions** first (Ideas), then open an issue/PR.

## Reporting a bug (Issues)

Before opening an issue:
- Search existing issues/discussions.
- Test on the latest release (or `main` if you can).

Include:
- Expected vs actual behavior
- TKeeper version / commit SHA
- Minimal reproduction steps (copy-pasteable)
- Logs/stack traces (don't forget to remove secrets if present)
- Environment (OS, JDK)

If you can provide a minimal failing test, even better.

## Testing expectations

- If your change affects behavior, **add or update an integration test**. See [integration tests](integration-tests)
- If you're not sure whether something is “behavioral”, assume it is and add the test.

## Code style

- Prefer small PRs with one clear purpose.
- Add tests for behavior changes when practical.
- Don’t mix large refactors with bug fixes. Keep fixes small and reviewable.
- Keep public API changes explicit.

## Commit messages

Use short, clear commit messages that describe the change. Prefixes such as `feat:`, `fix:`, or `chore:` are not required.

## Pull requests

A PR should include:
- What changed (short summary)
- Why it changed (rationale)
- Tests added/updated (or why not)
- Notes on compatibility and security impact (if applicable)

## License

By contributing, you agree that your contributions will be licensed under the project [Apache 2.0](LICENSE.md) license.