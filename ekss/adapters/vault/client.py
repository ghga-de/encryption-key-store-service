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


from typing import Union

import hvac


class VaultClient(hvac.Client):
    """Wrapper around hvac client delegating actions"""

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
