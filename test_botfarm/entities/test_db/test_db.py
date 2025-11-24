import pathlib

import pytest

from botfarm.entities import constants, db
from test_botfarm import conftest


@pytest.mark.parametrize(
    'file_name, expected_exception, expected_credentials',
    [
        pytest.param(
            constants.SETTINGS_FILE,
            None,
            {
                db.DBCredentialsEnvFields.user.name: conftest.DB_USER,
                db.DBCredentialsEnvFields.password.name: conftest.DB_PASSWORD,
                db.DBCredentialsEnvFields.host.name: conftest.DB_HOST,
                db.DBCredentialsEnvFields.port.name: conftest.DB_PORT,
                db.DBCredentialsEnvFields.get_name_field(): conftest.DB_NAME,
            },
        ),
        pytest.param('wrong_key.env', KeyError, None),
    ]
)
def test_from_env_file(file_name, expected_exception, expected_credentials, get_file_path):
    env_file = get_file_path(file_name)
    if expected_exception:
        with pytest.raises(expected_exception):
            db.DBCredentials.from_env_file(
                pathlib.Path(env_file), db.DBCredentialsEnvFields)
    else:
        assert db.DBCredentials.from_env_file(pathlib.Path(
            env_file), db.DBCredentialsEnvFields) == db.DBCredentials(**expected_credentials)
