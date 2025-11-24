import pytest

from botfarm.components import utils
from botfarm.entities import constants
from botfarm.entities import db


@pytest.mark.parametrize(
    'file_name, expected_env, expected_exception',
    [
        pytest.param('missing.env', None, FileNotFoundError),
        pytest.param(
            constants.SETTINGS_FILE,
            {
                db.DBCredentialsEnvFields.user.value: 'user',
                db.DBCredentialsEnvFields.password.value: 'password',
                db.DBCredentialsEnvFields.host.value: 'host',
                db.DBCredentialsEnvFields.port.value: '1',
                db.DBCredentialsEnvFields.name_.value: 'name',
            },
            None
        ),
    ],
)
def test_load_env(file_name, expected_env, expected_exception, get_file_path):
    env_path = get_file_path(file_name)
    if expected_exception:
        with pytest.raises(expected_exception):
            utils.load_env(env_path)
    else:
        assert utils.load_env(env_path) == expected_env
