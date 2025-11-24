import pytest

from botfarm.components import utils
from botfarm.entities import constants, db


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


@pytest.mark.parametrize(
    'password, expected_hash',
    [
        pytest.param(
            'password',
            '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8',
        ),
        pytest.param(
            'abc123',
            '6ca13d52ca70c883e0f0bb101e425a89e8624de51db2d2392593af6a84118090',
        ),
    ],
)
def test_hash_password(password, expected_hash):
    assert utils.hash_password(password) == expected_hash
