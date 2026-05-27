# deployDoc

The static HTML documentation is built as part of the full documentation pipeline, which first
generates RST files from TRLC sources, test reports, and the tracing report, then runs Sphinx.

Run the pipeline from the `tools/` directory (one level above this folder):

## Windows

```cmd
cd tools
make_html.bat
```

## Linux

```bash
cd tools
./make_html.sh
```

An optional `online` argument enables online report generation (used in CI):

```bash
./make_html.sh online
```

The generated HTML is written to `tools/deployDoc/build/html/`.

> **Note:** Do not run `make html` directly inside this folder — the required RST input files
> will be missing and Sphinx will produce warnings and incomplete output.
