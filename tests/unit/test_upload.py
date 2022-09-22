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

"""Test dummy."""


import pytest

from encryption_key_store.core.envelope_decryption import extract_envelope_content
from encryption_key_store.core.mongo_dao import get_ghga_secret_key, insert_file_secret

from ..fixtures.file_fixture import first_part_fixture  # noqa: F401
from ..fixtures.file_fixture import FirstPartFixture
from ..fixtures.ghga_secrets import generate_secrets_fixture  # noqa: F401
from ..fixtures.ghga_secrets import ghga_secrets_dao_fixture  # noqa: F401


@pytest.mark.asyncio
async def test_extract(
    *,
    first_part_fixture: FirstPartFixture,  # noqa: F811
):
    """Test envelope extraction/file secret insertion"""
    config = first_part_fixture.ghga_secrets_dao_fixture.config
    known_secret_id = first_part_fixture.ghga_secrets_dao_fixture.secret_id

    ghga_secret = await get_ghga_secret_key(id_=known_secret_id, config=config)
    file_secret, offset = await extract_envelope_content(
        file_part=first_part_fixture.content, ghga_secret=ghga_secret
    )
    secret_id = await insert_file_secret(file_secret=file_secret, config=config)

    result = (file_secret, secret_id, offset)
    assert all(result)
    assert offset > 0
