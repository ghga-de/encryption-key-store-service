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
"""
Provides DAOs for insertion/retrieval to/from MongoDB and wrappers around this functionality
"""

import base64
from typing import Tuple, Type, Union

from hexkit.protocols.dao import DaoSurrogateId
from hexkit.providers.mongodb import MongoDbConfig, MongoDbDaoFactory

from encryption_key_store.config import CONFIG
from encryption_key_store.core.file_secrets_db import (
    FileSecretCreationDto,
    FileSecretDto,
)
from encryption_key_store.core.ghga_secrets_db import (
    GHGASecretCreationDto,
    GHGASecretDto,
)


async def get_dao(
    *,
    name: str,
    dto_model: Union[Type[FileSecretDto], Type[GHGASecretDto]],
    dto_creation_model: Union[Type[FileSecretCreationDto], Type[GHGASecretCreationDto]],
    config: MongoDbConfig = CONFIG
) -> DaoSurrogateId:
    """Get a DAO for either file or GHGA secrets"""
    dao_factory = MongoDbDaoFactory(config=config)
    return await dao_factory.get_dao(
        name=name,
        dto_model=dto_model,
        dto_creation_model=dto_creation_model,
        id_field="id",
    )


async def get_file_secret_dao(*, config: MongoDbConfig = CONFIG) -> DaoSurrogateId:
    """Instantiate a DAO for file secret interactions"""
    return await get_dao(
        name="file_secrets",
        dto_model=FileSecretDto,
        dto_creation_model=FileSecretCreationDto,
        config=config,
    )


async def get_ghga_secret_dao(*, config: MongoDbConfig = CONFIG) -> DaoSurrogateId:
    """Instantiate a DAO for GHGA secret interactions"""
    return await get_dao(
        name="ghga_secrets",
        dto_model=GHGASecretDto,
        dto_creation_model=GHGASecretCreationDto,
        config=config,
    )


async def get_file_secret(id_: str, config: MongoDbConfig = CONFIG) -> bytes:
    """Retrieve file secret from db"""
    dao = await get_file_secret_dao(config=config)
    response = await dao.get(id_=id_)
    return base64.b64decode(response.file_secret)


async def insert_file_secret(file_secret: bytes, config: MongoDbConfig = CONFIG) -> str:
    """Encode and insert file secret into db"""
    file_secret = base64.b64encode(file_secret)
    file_secret_dto = FileSecretCreationDto(file_secret=file_secret)
    dao = await get_file_secret_dao(config=config)
    response = await dao.insert(file_secret_dto)
    return response.id


async def get_ghga_keypair(
    id_: str, config: MongoDbConfig = CONFIG
) -> Tuple[bytes, bytes]:
    """Retriever GHA keypair from db"""
    dao = await get_ghga_secret_dao(config=config)
    response = await dao.get(id_=id_)
    return base64.b64decode(response.public_key), base64.b64decode(response.private_key)


async def get_ghga_public_key(id_: str, config: MongoDbConfig = CONFIG) -> bytes:
    """Retrieve GHGA public key by ID"""
    keypair = await get_ghga_keypair(id_=id_, config=config)
    return keypair[0]


async def get_ghga_secret_key(id_: str, config: MongoDbConfig = CONFIG) -> bytes:
    """Retrieve GHGA secret key by ID"""
    keypair = await get_ghga_keypair(id_=id_, config=config)
    return keypair[1]


async def find_one_ghga_secret_key(config: MongoDbConfig = CONFIG) -> bytes:
    """Find one GHGA secret key"""
    dao = await get_ghga_secret_dao(config=config)
    match_all = {"$regex": ".*"}
    result = await dao.find_one(mapping={"id": match_all})
    return base64.b64decode(result.private_key)


async def insert_ghga_keypair(
    public_key: bytes, private_key: bytes, config: MongoDbConfig = CONFIG
) -> str:
    """Encode and insert GHGA keypair into DB"""
    public_key = base64.b64encode(public_key)
    private_key = base64.b64encode(private_key)
    ghga_secret_dto = GHGASecretCreationDto(
        public_key=public_key, private_key=private_key
    )
    dao = await get_ghga_secret_dao(config=config)
    response = await dao.insert(ghga_secret_dto)
    return response.id
