"""
Global fixures for tests.
"""
# Copyright CFHT/CNRS/CEA/UParisSaclay
# Licensed under the MIT licence

from os.path import join

import pytest



@pytest.fixture(autouse=True)
def tmp_config_filename(tmp_path_factory) -> str:
    """
    Generate a tempory configuration filename.

    Returns
    -------
    config_dir: str
        Temporary configuration directory name.
    """
    return str(join(tmp_path_factory.mktemp('config'), 'test.conf'))


