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

from .dao_keypair import dao_keypair_fixture  # noqa: F401
from .dao_keypair import generate_keypair_fixture  # noqa: F401
from .dao_keypair import DaoKeypairFixture, KeypairFixture


@dataclass
class FirstPartFixture:
    """Fixture for envelope extraction"""

    client_pubkey: bytes
    content: bytes
    dao_keypair_fixture: DaoKeypairFixture


@pytest_asyncio.fixture
async def first_part_fixture(
    *,
    dao_keypair_fixture: DaoKeypairFixture,  # noqa: F811
    generate_keypair_fixture: KeypairFixture,  # noqa: F811
) -> AsyncGenerator[FirstPartFixture, None]:
    """
    Create random File, encrypt with Crypt4GH, return DAOs, secrets and first file part
    """
    file_size = 20 * 1024**2
    part_size = 16 * 1024**2

    with big_temp_file(file_size) as raw_file:
        with io.BytesIO() as encrypted_file:
            server_public = dao_keypair_fixture.keypair.public_key
            keys = [(0, generate_keypair_fixture.private_key, server_public)]
            # rewind input file for reading
            raw_file.seek(0)
            crypt4gh.lib.encrypt(keys=keys, infile=raw_file, outfile=encrypted_file)
            # rewind output file for reading
            encrypted_file.seek(0)
            part = encrypted_file.read(part_size)
            yield FirstPartFixture(
                client_pubkey=generate_keypair_fixture.public_key,
                content=part,
                dao_keypair_fixture=dao_keypair_fixture,
            )
