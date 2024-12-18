import os
from dotenv import dotenv_values, find_dotenv, load_dotenv

# TODO encrypt this


class Config:
    """
    A configuration class that loads environment variables from a .env file
    and provides secure access to them.
    """

    def __init__(self, env_file=None):
        """
        Initializes the Config class.

        Args:
            env_file (str, optional): Path to the .env file. If None, find_dotenv
                                     will be used to locate it. Defaults to None.
        """
        self.env_file = env_file or find_dotenv(usecwd=True)
        if not self.env_file:
            raise FileNotFoundError("Could not find .env file")
        self._load_config()

    def set_env_vars(self):
        """
        Sets env attributes
        """
        load_dotenv(self.env_file)

    def _load_config(self):
        """
        Sets env attributes
        Loads environment variables from the .env file and dynamically sets them as attributes.
        """
        load_dotenv(self.env_file)
        config_data = dotenv_values(self.env_file)
        for key, value in config_data.items():
            setattr(self, key, value)

    def __getattr__(self, name):
        """
        Handles attribute access for undefined attributes, raising an error.

        Args:
            name (str): The name of the attribute.

        Returns:
            Any: The value of the attribute.

        Raises:
            AttributeError: If the attribute is not found.
        """
        raise AttributeError(f"'Config' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        """
        Securely sets attributes, preventing modification of existing config values,
        unless they are private (start with '_').

        Args:
            name (str): The name of the attribute.
            value (Any): The value to set.

        Raises:
            TypeError: If attempting to modify an existing configuration attribute.
        """
        if name.startswith("_") or name == "env_file":
            # Allow setting private attributes or env_file
            super().__setattr__(name, value)
        elif hasattr(self, name):
            raise TypeError(f"Cannot modify existing configuration attribute '{name}'")
        else:
            super().__setattr__(name, value)
