# Tools <!-- omit in toc -->

The documentation of pyTRLCConverter (requirements, architecture, detailed design,
tests, test results, tracing report and coverage report) is built by
[trlcdoc](https://github.com/nhjschulz/trlc-doc), configured in
[trlcdoc.yaml](../trlcdoc.yaml) in the project root. The following tools support it:

- [Documentation build](#documentation-build)
- [converter](#converter)
- [trlc2other](#trlc2other)

## Documentation build

```bash
pip install -r requirements-dev.txt    # installs trlcdoc
pip install -e .                       # document this pyTRLCConverter, not the PyPI release
trlcdoc                                # all steps, site in build/trlcdoc/html
trlcdoc --online                       # tracing report linked to GitHub (used for deployment)
trlcdoc trace                          # selected steps only, e.g. the tracing report
trlcdoc clean                          # remove all build artifacts
```

trlcdoc runs the tests with coverage, converts the TRLC files with the project converters,
creates the LOBSTER tracing report and builds the Sphinx site. PlantUML is taken from the
`PLANTUML` environment variable (jar or server URL) or downloaded on demand. Java and Graphviz
must be installed.

The project owned Sphinx sources are in [doc/sphinx](../doc/sphinx): the start page, the
detailed design, the page header and the Sphinx configuration with the version selector
of the deployed documentation.

Exit codes: `0` success, `1` content findings (failed tests, missing trace links), `2` build
error.

## converter

The project converters for the pyTRLCConverter model files, used by trlcdoc and by
trlc2other.

[Details](./converter/README.md)

## trlc2other

Exports the requirements, architecture and test cases as docx and ReqIF files.

[Details](./trlc2other/README.md)
