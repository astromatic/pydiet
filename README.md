# pyDIET

[![Documentation](https://github.com/astromatic/pydiet/actions/workflows/doc.yml/badge.svg)](https://astromatic.github.io/pydiet/)
[![Tests](https://github.com/astromatic/pydiet/actions/workflows/tests.yml/badge.svg)](https://github.com/astromatic/pydiet/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/astromatic/pydiet/graph/badge.svg?token=q4ZbXlhZNC)](https://codecov.io/gh/astromatic/pydiet)

[CFHT](https://www.cfht.hawaii.edu)'s new Direct Imaging Exposure Time calculator.

# Docker Notes
To build the a Dockerfile for installing pyDiet:
```
docker build -t pydiet:latest -f docker/Dockerfile .
```

Run, get a shell, and python venv
```
docker run -tid --name pydiet pydiet
docker exec -ti pydiet "/bin/bash"
source venv_pydiet/bin/activate
```
