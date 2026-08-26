# skinner

**Coming soon.** Nothing here does anything yet.

`skinner` is a Python project in the earliest possible state: a package that imports, a
task runner, and the conventions it expects of anyone working in it. Everything else is
still to be built.

## Planned

- **ASCII slugs** — normalize a name to a URL-safe ASCII slug, so `Крипто Проект`
  becomes `kripto-proekt`. Planned via [Unidecode](https://pypi.org/project/Unidecode/).

## Getting started

```bash
just setup
```

`uv` manages the application; `just` manages the project. `just check` lints and
formats, `just test` runs the suite.

## License

MIT
