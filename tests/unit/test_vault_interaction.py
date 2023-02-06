# Copyright 2021 - 2023 Universität Tübingen, DKFZ, EMBL, and Universität zu Köln
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

import os

from tests.fixtures.vault import vault_fixture  # noqa: F401
from tests.fixtures.vault import VaultFixture


def test_connection(vault_fixture: VaultFixture):  # noqa: F811
    """Test if container is up and reachable"""

    secret = os.urandom(32)
    secret_id = vault_fixture.adapter.store_secret(secret=secret)
    stored_secret = vault_fixture.adapter.get_secret(key=secret_id)
    assert secret == stored_secret
