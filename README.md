# PyDIET

[![Documentation](https://github.com/astromatic/pydiet/actions/workflows/doc.yml/badge.svg)](https://astromatic.github.io/pydiet/)
[![Tests](https://github.com/astromatic/pydiet/actions/workflows/tests.yml/badge.svg)](https://github.com/astromatic/pydiet/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/astromatic/pydiet/graph/badge.svg?token=t3ZeGLnWTD)](https://codecov.io/gh/astromatic/pydiet)

PyDIET is [CFHT](https://www.cfht.hawaii.edu)'s new Direct Imaging Exposure Time calculator.

<p>
  <img src="https://github.com/astromatic/pydiet/blob/main/docs/src/figures/pydiet.jpg" alt="Screenshot" width="640"/>
</p>

## Important
PyDIET is still in testing phase.
The authors reserve the right to modify, update, or discontinue any aspect of the package at any time without notice.
This includes, but is not limited to, changes in instrument models, calibration data, algorithms, or implementation details, which may result in differences in the outputs produced by PyDIET over time.

The authors shall not be liable for any direct, indirect, incidental, consequential, or special damages arising out of or in connection with the use of, or inability to use PyDIET including but not limited to errors in calculations, scientific results, or observational planning.

## Installing

### pip/pipx

```
git clone https://github.com/astromatic/pydiet
cd pydiet
pip install .
```

### Docker
To build a Dockerfile for installing pyDiet:
```
docker build -t pydiet:latest -f docker/Dockerfile .
```
Run, get a shell, and python venv
```
docker run -tid --name pydiet pydiet
docker exec -ti pydiet "/bin/bash"
source venv_pydiet/bin/activate
```
## Executing (locally)

```
pydiet -b
```

## Customizing
PyDIET can easily be adapted to other astronomical imagers by simply editing the [``data/data_config.toml``](https://github.com/astromatic/pydiet/blob/main/src/pydiet/data/data_config.toml) file in [TOML](https://toml.io) format, and supplying [pysynphot-compliant](https://pysynphot.readthedocs.io/en/latest/using_pysynphot.html#pysynphot-io) transmission/emission [FITS](https://en.wikipedia.org/wiki/FITS) files for the various parts of the instrument chain.
Use the provided [``utils/extract_filter.py`` script](https://github.com/astromatic/pydiet/blob/main/utils/extract_filter.py) to convert ASCII tables to pysynphot-compliant FITS format.

The web interface can easily be customized to accomodate one or several instruments through query form and result display [templates](https://github.com/astromatic/pydiet/tree/main/src/pydiet/templates).

