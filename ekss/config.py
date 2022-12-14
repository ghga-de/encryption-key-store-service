# Copyright 2021 - 2023 Universität Tübingen, DKFZ and EMBL
# for the German Human Genome-Phenome Archive (GHGA)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Config Parameter Modeling and Parsing"""

from ghga_service_chassis_lib.api import ApiConfigBase
from ghga_service_chassis_lib.config import config_from_yaml
from pydantic import BaseSettings, Field, SecretStr


class VaultConfig(BaseSettings):
    """Configuration for HashiCorp Vault connection"""

    vault_host: str = Field(
        ...,
        example="http://127.0.0.1",
        description="URL of the vault instance to connect to without port number",
    )
    vault_port: int = Field(
        ...,
        example="8200",
        description="Port number of the vault instance to connect to",
    )
    vault_token: SecretStr = Field(
        ...,
        example="dummy-token",
        description="Token used for authentication against HashiCorp Vault",
    )


@config_from_yaml(prefix="ekss")
class Config(ApiConfigBase, VaultConfig):
    """Config parameters and their defaults."""

    service_name: str = "encryption_key_store"
    server_private_key: SecretStr = Field(
        ...,
        example="server_private_key",
        description="Base64 encoded server Crypt4GH private key",
    )
    server_public_key: str = Field(
        ...,
        example="server_public_key",
        description="Base64 encoded server Crypt4GH public key",
    )


CONFIG = Config()
