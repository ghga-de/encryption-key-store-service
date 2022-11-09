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
"""Test HashiCorp Vault interaction"""

import pytest

from tests.fixtures.vault import vault_fixture  # noqa: F401
from tests.fixtures.vault import VaultFixture


@pytest.mark.asyncio
async def test_connection(vault_fixture: VaultFixture):  # noqa: F811
    """Test if container is up and reachable"""
    assert vault_fixture.client.is_authenticated()
