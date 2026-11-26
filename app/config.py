import os
import sys


# Preferred env var name. The old, mis-spelled name is kept as a fallback so
# existing self-hosted installations (Docker, systemd, RPM) keep working until
# operators migrate. A one-time warning is printed on startup if only the
# legacy name is set.
_CONFIG_ENV = "INCIDENTRELAY_CONFIG_FILE"
_LEGACY_CONFIG_ENV = "INCEDENTRELAY_CONFIG_FILE"
_DEFAULT_CONFIG_PATH = "/etc/incidentrelay/incidentrelay.conf"


def _resolve_config_path():
    """Return the configured config file path, preferring the non-typo env var."""
    value = os.getenv(_CONFIG_ENV)
    legacy = os.getenv(_LEGACY_CONFIG_ENV) if not value else None
    if legacy:
        print(
            f"WARNING: environment variable {_LEGACY_CONFIG_ENV} is deprecated "
            f"(typo); please use {_CONFIG_ENV} instead.",
            file=sys.stderr,
        )
    configured = value or legacy or _DEFAULT_CONFIG_PATH
    # docker exec starts with the image environment, not the environment
    # exported by entrypoint.sh. Use the generated shared config there too,
    # but never override an explicitly configured custom source path.
    runtime = os.getenv("INCIDENTRELAY_RUNTIME_CONFIG_FILE")
    if configured == _DEFAULT_CONFIG_PATH and runtime and os.path.isfile(runtime):
        return runtime

    return configured


CONFIG_FILE = _resolve_config_path()
