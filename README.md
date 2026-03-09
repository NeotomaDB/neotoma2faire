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

The script uses Python and the `uv` project management tool. With `uv` already installed, first, `sync` the project, to install all the necessary packages. Once the project is `sync`ed, then the project can be run:

```bash
uv run neotoma2faire [tool] -h -o <OUTPUT_FILE> -t <TEMPLATE_FILE> -d <DATASETID>
```

### Tools

* `template`: Currently the only tool implemented. The `template` tool will take a dataset ID and return the FAIRe template for that file.

### Flags

* `-h`, `--help`: Get help for the commandline operation.
* `-o`, `--output`: Define the output file to be used.

## Contributors

This project is an open project, and contributions are welcome from any individual.  All contributors to this project are bound by a [code of conduct](CODE_OF_CONDUCT.md).  Please review and follow this code of conduct as part of your contribution.

* [![ORCID](https://img.shields.io/badge/orcid-0000--0002--7926--4935-brightgreen.svg)](https://orcid.org/0000-0002-7926-4935) [Socorro Dominguez](https://ht-data.com/about)
* [![ORCID](https://img.shields.io/badge/orcid-0000--0002--2700--4605-brightgreen.svg)](https://orcid.org/0000-0002-2700-4605) [Simon Goring](http://www.goring.org)

### Tips for Contributing

Issues and bug reports are always welcome.  Code clean-up, and feature additions can be done either through pull requests to [project forks](https://github.com/NeotomaDB/neotoma2faire/network/members) or [project branches](https://github.com/NeotomaDB/neotoma2faire/branches).

Before submitting a pull request, please ensure that:

* All existing tests pass: `uv run pytest tests/`
* Code passes Ruff linting and formatting: `uv run ruff check src/` and `uv run ruff format --check src/`
* New functionality includes corresponding tests in the `tests/` directory

These checks are enforced automatically by the [CI workflow](.github/workflows/ci.yml) on every push and pull request.

Please direct development questions to Socorro Dominguez by email: [dominguezvid@wisc.edu](mailto:dominguezvid@wisc.edu).

All products of the Neotoma Paleoecology Database are licensed under an [MIT License](LICENSE.md) unless otherwise noted.
