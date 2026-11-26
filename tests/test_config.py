import pytest

from app import config


@pytest.fixture
def config_environment(monkeypatch):
    for name in (
        "INCIDENTRELAY_CONFIG_FILE",
        "INCEDENTRELAY_CONFIG_FILE",
        "INCIDENTRELAY_RUNTIME_CONFIG_FILE",
    ):
        monkeypatch.delenv(name, raising=False)
    return monkeypatch


@pytest.mark.parametrize("variable", [None, "INCIDENTRELAY_CONFIG_FILE", "INCEDENTRELAY_CONFIG_FILE"])
def test_default_source_uses_existing_runtime_config(config_environment, tmp_path, variable):
    runtime = tmp_path / "runtime.conf"
    runtime.write_text("[main]\nsecret_key = generated-key\n", encoding="utf-8")
    config_environment.setenv("INCIDENTRELAY_RUNTIME_CONFIG_FILE", str(runtime))
    if variable:
        config_environment.setenv(variable, config._DEFAULT_CONFIG_PATH)

    assert config._resolve_config_path() == str(runtime)


@pytest.mark.parametrize("variable", ["INCIDENTRELAY_CONFIG_FILE", "INCEDENTRELAY_CONFIG_FILE"])
def test_custom_config_is_not_replaced_by_runtime(config_environment, tmp_path, variable):
    runtime = tmp_path / "runtime.conf"
    runtime.touch()
    config_environment.setenv("INCIDENTRELAY_RUNTIME_CONFIG_FILE", str(runtime))
    config_environment.setenv(variable, "/custom/incidentrelay.conf")

    assert config._resolve_config_path() == "/custom/incidentrelay.conf"


def test_missing_runtime_uses_source_config(config_environment, tmp_path):
    config_environment.setenv("INCIDENTRELAY_RUNTIME_CONFIG_FILE", str(tmp_path / "missing.conf"))

    assert config._resolve_config_path() == config._DEFAULT_CONFIG_PATH


def test_runtime_is_not_selected_outside_image(config_environment):
    assert config._resolve_config_path() == config._DEFAULT_CONFIG_PATH


def test_preferred_config_variable_wins(config_environment):
    config_environment.setenv("INCIDENTRELAY_CONFIG_FILE", "/custom/preferred.conf")
    config_environment.setenv("INCEDENTRELAY_CONFIG_FILE", "/custom/legacy.conf")

    assert config._resolve_config_path() == "/custom/preferred.conf"
