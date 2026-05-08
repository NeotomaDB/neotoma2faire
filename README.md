<!-- badges: start -->
[![lifecycle](https://img.shields.io/badge/lifecycle-stable-green.svg)](https://lifecycle.r-lib.org/articles/stages.html#stable)
[![NSF-](https://img.shields.io/badge/NSF--blue.svg)](https://www.nsf.gov/awardsearch/showAward?AWD_ID=)
[![NSF-](https://img.shields.io/badge/NSF--blue.svg)](https://www.nsf.gov/awardsearch/showAward?AWD_ID=)

[![DOI](https://zenodo.org/badge/.svg)](https://doi.org/10.5281/zenodo.)
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects//badge)](https://www.bestpractices.dev/projects/)
[![CI](https://github.com/NeotomaDB/neotoma2faire/actions/workflows/ci.yml/badge.svg)](https://github.com/NeotomaDB/neotoma2faire/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/NeotomaDB/neotoma2faire/branch/main/graph/badge.svg)](https://codecov.io/gh/NeotomaDB/neotoma2faire)
<!-- badges: end -->

# neotoma2 FAIRe

This script is intended to support the generation of FAIRe files from the Neotoma API. The goal is to write this as a simple Python package that uses the core Neotoma API endpoints to generate a FAIRe XLSX spreadsheet from the existing (and new) API endpoints to ensure users can submit and extract FAIRe data from Neotoma as aeDNA data is added to the database.

The goal is to produce a script that will allow a user to submit a datasetid and recieve back a FAIRe formatted spreadsheet with all the appropriate fields filled in.

## Using this repository

The script uses Python and the `uv` project management tool.

### Setup

1. Install `uv` and clone this repository.
2. Sync the project to install all dependencies:
   ```bash
   uv sync
   ```
3. Copy `.env.example` to `.env.production` and `.env.dev`, then fill in any
   credentials you need (e.g. the `DBAUTH` and `DBAUTH_TEST` JSON strings used
   by the imagined-table queries). Both files are gitignored.

### Running the tool

```bash
uv run python neo2faire.py template -d <DATASETID> -o <OUTPUT_FILE> -t <TEMPLATE_FILE>
```

You can also run it through the installed entry point:

```bash
uv run neotoma2faire template -d <DATASETID> -o <OUTPUT_FILE> -t <TEMPLATE_FILE>
```

### Tools

* `template`: Currently the only tool implemented. The `template` tool will take a dataset ID and return the FAIRe template for that file.

### Flags

* `-h`, `--help`: Show help for the command line tool.
* `-o`, `--output`: Output `.xlsx` path. Default: `template.xlsx`.
* `-t`, `--template`: Path to the base FAIRe template workbook. Default:
  `./assets/FAIRe_checklist_v1.0.2_FULLtemplate.xlsx`.
* `-d`, `--dataset`: Neotoma dataset ID to convert. Default: `55582`.
* `-e`, `--env {prod,dev}`: Explicitly choose which Neotoma REST API to hit.
  Defaults to `NEOTOMA_API_ENV` (set by the `.env` file) or `prod`.
* `--dev`: Shortcut for the dev environment — loads `.env.dev` and points the
  API client at `api-dev.neotomadb.org`. Without this flag, `.env.production`
  is loaded and the public API is used.
* `-v`, `--version`: Print the program version and exit.

### Environments (prod / dev)

Neotoma exposes two REST environments and the package can target either:

* **prod** — `https://api.neotomadb.org/v2.0/data` (public API, default).
* **dev**  — `https://api-dev.neotomadb.org/v2.0/data` (staging; new endpoints
  ship here first).

Default run uses production:
```bash
uv run python neo2faire.py template -d 55582
```

Use `--dev` to load `.env.dev` and hit the development API:
```bash
uv run python neo2faire.py template -d 74029 --dev
```

## Contributors

This project is an open project, and contributions are welcome from any individual.  All contributors to this project are bound by a [code of conduct](CODE_OF_CONDUCT.md).  Please review and follow this code of conduct as part of your contribution.

* [![ORCID](https://img.shields.io/badge/orcid-0000--0002--7926--4935-brightgreen.svg)](https://orcid.org/0000-0002-7926-4935) [Socorro Dominguez](https://ht-data.com/about)
* [![ORCID](https://img.shields.io/badge/orcid-0000--0002--2700--4605-brightgreen.svg)](https://orcid.org/0000-0002-2700-4605) [Simon Goring](http://www.goring.org)

### Tips for Contributing

Issues and bug reports are always welcome.  Code clean-up, and feature additions can be done either through pull requests to [project forks](https://github.com/NeotomaDB/neotoma2faire/network/members) or [project branches](https://github.com/NeotomaDB/neotoma2faire/branches).

Before submitting a pull request, please ensure that:

* All existing tests pass: `uv run python -m pytest tests/`
* Code passes Ruff linting and formatting: `uv run ruff check src/` and `uv run ruff format --check src/`
* New functionality includes corresponding tests in the `tests/` directory

These checks are enforced automatically by the [CI workflow](.github/workflows/ci.yml) on every push and pull request.

Please direct development questions to Socorro Dominguez by email: [dominguezvid@wisc.edu](mailto:dominguezvid@wisc.edu).

All products of the Neotoma Paleoecology Database are licensed under an [MIT License](LICENSE.md) unless otherwise noted.
