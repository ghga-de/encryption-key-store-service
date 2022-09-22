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

from encryption_key_store.core.db_interop.file_secrets_db import (
    FileSecretCreationDto,
    FileSecretDto,
)
from encryption_key_store.core.db_interop.ghga_secrets_db import (
    GHGASecretCreationDto,
    GHGASecretDto,
)


class MongoDbDao:
    """abstractions over file secret/GHGA secret DAOs"""

    def __init__(self, config: MongoDbConfig):
        self.config = config

    async def get_dao(
        self,
        *,
        name: str,
        dto_model: Union[Type[FileSecretDto], Type[GHGASecretDto]],
        dto_creation_model: Union[
            Type[FileSecretCreationDto], Type[GHGASecretCreationDto]
        ]
    ) -> DaoSurrogateId:
        """Get a DAO for either file or GHGA secrets"""
        dao_factory = MongoDbDaoFactory(config=self.config)
        return await dao_factory.get_dao(
            name=name,
            dto_model=dto_model,
            dto_creation_model=dto_creation_model,
            id_field="id",
        )

    async def get_file_secret_dao(self) -> DaoSurrogateId:
        """Instantiate a DAO for file secret interactions"""
        return await self.get_dao(
            name="file_secrets",
            dto_model=FileSecretDto,
            dto_creation_model=FileSecretCreationDto,
        )

    async def get_ghga_secret_dao(self) -> DaoSurrogateId:
        """Instantiate a DAO for GHGA secret interactions"""
        return await self.get_dao(
            name="ghga_secrets",
            dto_model=GHGASecretDto,
            dto_creation_model=GHGASecretCreationDto,
        )

    async def get_file_secret(self, *, id_: str) -> bytes:
        """Retrieve file secret from db"""
        dao = await self.get_file_secret_dao()
        response = await dao.get(id_=id_)
        return base64.b64decode(response.file_secret)

    async def insert_file_secret(self, *, file_secret: bytes) -> str:
        """Encode and insert file secret into db"""
        file_secret = base64.b64encode(file_secret)
        file_secret_dto = FileSecretCreationDto(file_secret=file_secret)
        dao = await self.get_file_secret_dao()
        response = await dao.insert(file_secret_dto)
        return response.id

    async def get_ghga_keypair(self, *, id_: str) -> Tuple[bytes, bytes]:
        """Retriever GHA keypair from db"""
        dao = await self.get_ghga_secret_dao()
        response = await dao.get(id_=id_)
        return base64.b64decode(response.public_key), base64.b64decode(
            response.private_key
        )

    async def get_ghga_public_key(self, *, id_: str) -> bytes:
        """Retrieve GHGA public key by ID"""
        keypair = await self.get_ghga_keypair(id_=id_)
        return keypair[0]

    async def get_ghga_secret_key(self, *, id_: str) -> bytes:
        """Retrieve GHGA secret key by ID"""
        keypair = await self.get_ghga_keypair(id_=id_)
        return keypair[1]

    async def find_one_ghga_secret_key(self) -> Tuple[bytes, str]:
        """
        Find GHGA secret key. Assume we only have one and also return ID for later reuse
        """
        dao = await self.get_ghga_secret_dao()
        match_all = {"$regex": ".*"}
        # apparently can't match on id, use another one instead
        result = await dao.find_one(mapping={"private_key": match_all})
        return base64.b64decode(result.private_key), result.id

    async def insert_ghga_keypair(
        self, *, public_key: bytes, private_key: bytes
    ) -> str:
        """Encode and insert GHGA keypair into DB"""
        public_key = base64.b64encode(public_key)
        private_key = base64.b64encode(private_key)
        ghga_secret_dto = GHGASecretCreationDto(
            public_key=public_key, private_key=private_key
        )
        dao = await self.get_ghga_secret_dao()
        response = await dao.insert(ghga_secret_dto)
        return response.id
