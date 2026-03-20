import os
from abc import ABC, abstractmethod
from typing import Optional

class SecretManager(ABC):
    @abstractmethod
    def get_secret(self, key: str) -> Optional[str]:
        pass

class LocalSecretManager(SecretManager):
    """Reads secrets from Environment Variables (loaded from .env)."""
    def get_secret(self, key: str) -> Optional[str]:
        return os.getenv(key)

class AWSSecretManagerStub(SecretManager):
    """Stub for future AWS Secrets Manager implementation."""
    def get_secret(self, key: str) -> Optional[str]:
        # TODO: Implement boto3 call
        pass

def get_secret(key: str) -> str:
    """Helper to get secret from active manager."""
    # Logic to decide which manager to use could be Env based
    manager = LocalSecretManager() 
    val = manager.get_secret(key)
    if val is None:
        return ""
    return val
