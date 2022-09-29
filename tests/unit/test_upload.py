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

"""Unit tests for upload functionality"""

import pytest

from ekss.core.envelope_decryption import extract_envelope_content, store_secret

from ..fixtures.config_override import ConfigOverride
from ..fixtures.dao_keypair import dao_fixture  # noqa: F401
from ..fixtures.dao_keypair import generate_keypair_fixture  # noqa: F401
from ..fixtures.file_fixture import first_part_fixture  # noqa: F401
from ..fixtures.file_fixture import FirstPartFixture


@pytest.mark.asyncio
async def test_extract(
    *,
    first_part_fixture: FirstPartFixture,  # noqa: F811
):
    """Test envelope extraction/file secret insertion"""
    with ConfigOverride():
        client_pubkey = first_part_fixture.client_pubkey
        dao = first_part_fixture.dao

        file_secret, offset = await extract_envelope_content(
            file_part=first_part_fixture.content,
            client_pubkey=client_pubkey,
        )
        stored_secret = await store_secret(file_secret=file_secret[::-1], dao=dao)
        # stored_secret = await store_secret(file_secret=file_secret, dao=dao)
        result = (file_secret, stored_secret.id, offset)

    assert all(result)
    assert offset > 0
