import pytest

from src.config import ConfigError, load_config


def write_config(tmp_path, text):
    path = tmp_path / "config.yaml"
    path.write_text(text, encoding="utf-8")
    return str(path)


def test_load_config_valid(tmp_path):
    config = load_config(write_config(
        tmp_path,
        "package_name: 'test:test'\n"
        "repo_url: './test_repo'\n"
        "test_mode: true\n"
        "version: '1.0'\n"
        "max_depth: 2\n",
    ))
    assert config.package_name == "test:test"
    assert config.test_mode is True
    assert config.max_depth == 2


def test_missing_file(tmp_path):
    with pytest.raises(ConfigError):
        load_config(str(tmp_path / "missing.yaml"))


def test_invalid_depth(tmp_path):
    with pytest.raises(ConfigError):
        load_config(write_config(
            tmp_path,
            "package_name: 'test:test'\n"
            "repo_url: './test_repo'\n"
            "test_mode: true\n"
            "version: '1.0'\n"
            "max_depth: -1\n",
        ))


def test_invalid_package_name(tmp_path):
    with pytest.raises(ConfigError):
        load_config(write_config(
            tmp_path,
            "package_name: 'invalid'\n"
            "repo_url: './test_repo'\n"
            "test_mode: true\n"
            "version: '1.0'\n"
            "max_depth: 2\n",
        ))
