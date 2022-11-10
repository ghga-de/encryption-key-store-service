# Copyright 2021 - 2022 Universität Tübingen, DKFZ and EMBL
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
"""Provides client side functionality for interaction with HashiCorp Vault"""

import base64
from typing import Union
from uuid import uuid4

import hvac
import hvac.exceptions

from ekss.adapters.outbound.vault import exceptions


class VaultClient(hvac.Client):
    """Custom hvac client delegating actions"""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        url: str,
        token: str,
        namespace: str = "vault",
        verify: Union[bool, str] = True,
        timeout: int = 15,
    ):
        super().__init__(
            url=url,
            namespace=namespace,
            token=token,
            verify=verify,
            timeout=timeout,
        )
        self.secrets.kv.default_kv_version = 2

    def store_secret(self, *, secret: bytes, prefix: str = "ekss") -> str:
        """
        Store a secret under a subpath of the given prefix.
        Generates a UUID4 as key, uses it for the subpath and returns it.
        """
        key = str(uuid4())
        value = base64.b64encode(secret).decode("utf-8")

        try:
            # set cas to 0 as we only want a static secret
            self.secrets.kv.create_or_update_secret(
                path=f"{prefix}/{key}", secret={key: value}, cas=0
            )
        except hvac.exceptions.InvalidRequest as exc:
            raise exceptions.SecretInsertionError() from exc
        return key

    def get_secret(self, *, key: str, prefix: str = "ekss") -> bytes:
        """
        Retrieve a secret at the subpath of the given prefix denoted by key.
        Key should be a UUID4 returned by store_secret on insertion
        """
        try:
            response = self.secrets.kv.read_secret_version(path=f"{prefix}/{key}")
        except hvac.exceptions.InvalidRequest as exc:
            raise exceptions.SecrertRetrievalError() from exc

        secret = response["data"]["data"][key]
        return base64.b64decode(secret)
