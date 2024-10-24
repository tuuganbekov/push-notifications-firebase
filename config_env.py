import platform

if platform.system().lower() == "windows":
    ENV_FILE = "vault/secrets/env"
else:
    ENV_FILE = "/vault/secrets/env"


class ConfigFile:
    def __init__(self):
        env = {}
        with open(ENV_FILE, "r") as f:  # mypy: ignore-errors
            for line in f.readlines():
                key, value = line.strip().split(": ")
                env[key.strip()] = value.strip()
        self.vars = env

    def __call__(self, name, default=None):
        env_value = self.vars.get(name, default)
        return env_value

    def list(self, name, default=None):
        list_vars = self.vars.get(name)
        if list_vars:
            return list_vars.split(",")
        return default

    def bool(self, name, default=None):
        bool_vars = self.vars.get(name, default)
        return bool_vars
