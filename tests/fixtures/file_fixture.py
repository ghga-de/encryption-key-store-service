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


import io
from dataclasses import dataclass
from typing import AsyncGenerator

import crypt4gh.lib
import pytest_asyncio
from ghga_service_chassis_lib.utils import big_temp_file

from encryption_key_store.core.mongo_dao import get_ghga_public_key

from .ghga_secrets import generate_secrets_fixture  # noqa: F401
from .ghga_secrets import ghga_secrets_dao_fixture  # noqa: F401
from .ghga_secrets import GenerateSecretsFixture, GHGASecretsDaoFixture


@dataclass
class FirstPartFixture:
    """Fixture for envelope extraction"""

    content: bytes
    ghga_secrets_dao_fixture: GHGASecretsDaoFixture


@pytest_asyncio.fixture
async def first_part_fixture(
    *,
    ghga_secrets_dao_fixture: GHGASecretsDaoFixture,  # noqa: F811
    generate_secrets_fixture: GenerateSecretsFixture,  # noqa: F811
) -> AsyncGenerator[FirstPartFixture, None]:
    """
    Create random File, encrypt with Crypt4GH, return DAOs, secrets and first file part
    """
    file_size = 20 * 1024**2
    part_size = 16 * 1024**2

    with big_temp_file(file_size) as raw_file:
        with io.BytesIO() as encrypted_file:
            ghga_public = await get_ghga_public_key(
                id_=ghga_secrets_dao_fixture.secret_id,
                config=ghga_secrets_dao_fixture.config,
            )
            keys = [(0, generate_secrets_fixture.private_key, ghga_public)]
            # rewind input file for reading
            raw_file.seek(0)
            crypt4gh.lib.encrypt(keys=keys, infile=raw_file, outfile=encrypted_file)
            # rewind output file for reading
            encrypted_file.seek(0)
            part = encrypted_file.read(part_size)
            yield FirstPartFixture(
                content=part, ghga_secrets_dao_fixture=ghga_secrets_dao_fixture
            )
