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
"""Provides a fixture around MongoDB, prefilling the DB with test data"""

from dataclasses import dataclass
from typing import AsyncGenerator

import pytest_asyncio
from crypt4gh.keys import get_private_key, get_public_key
from crypt4gh.keys.c4gh import generate as generate_keypair
from hexkit.providers.mongodb import MongoDbConfig
from hexkit.providers.mongodb.testutils import config_from_mongodb_container
from testcontainers.mongodb import MongoDbContainer

from encryption_key_store.core.mongo_dao import insert_ghga_keypair


@dataclass
class GenerateSecretsFixture:
    """Fixture containing a keypair"""

    public_key: bytes
    private_key: bytes


@dataclass
class GHGASecretsDaoFixture:
    """
    Fixture containing config for DAOs and the ID of the GHGA secret inserted
    """

    config: MongoDbConfig
    secret_id: str


@pytest_asyncio.fixture
async def generate_secrets_fixture(
    tmp_path,
) -> AsyncGenerator[GenerateSecretsFixture, None]:
    """Creates a keypair using crypt4gh"""
    # Crypt4GH always writes to file
    public_key_file = tmp_path / "public.key"
    private_key_file = tmp_path / "private.key"
    generate_keypair(seckey=private_key_file, pubkey=public_key_file)
    public_key = get_public_key(public_key_file)
    private_key = get_private_key(private_key_file, lambda: None)
    yield GenerateSecretsFixture(public_key=public_key, private_key=private_key)


@pytest_asyncio.fixture
async def ghga_secrets_dao_fixture(
    *,
    generate_secrets_fixture,  # pylint: disable=redefined-outer-name
) -> AsyncGenerator[GHGASecretsDaoFixture, None]:
    """
    Pytest fixture for tests depending on the MongoDbDaoFactory DAO with GHGA secret
    already inserted.
    """
    with MongoDbContainer(image="mongo:5.0.11") as mongodb:
        config = config_from_mongodb_container(mongodb)

        secret_id = await insert_ghga_keypair(
            public_key=generate_secrets_fixture.public_key,
            private_key=generate_secrets_fixture.private_key,
            config=config,
        )
        yield GHGASecretsDaoFixture(config=config, secret_id=secret_id)
