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
"""Checking if POST on /secrets works correctly"""
import base64
import codecs
import os

import pytest
from fastapi.testclient import TestClient

from encryption_key_store.api.main import app
from encryption_key_store.api.upload.router import dao_injector
from encryption_key_store.core.db_interop.ghga_secrets_db import GHGASecretCreationDto
from encryption_key_store.core.db_interop.mongo_dao import MongoDbDao

from ..fixtures.file_fixture import first_part_fixture  # noqa: F401
from ..fixtures.file_fixture import FirstPartFixture
from ..fixtures.ghga_secrets import generate_secrets_fixture  # noqa: F401
from ..fixtures.ghga_secrets import ghga_secrets_dao_fixture  # noqa: F401

client = TestClient(app=app)


@pytest.mark.asyncio
async def test_post_secrets(
    *,
    first_part_fixture: FirstPartFixture,  # noqa: F811
):
    """Test request response for /secrets endpoint with valid data"""

    async def dao_override() -> MongoDbDao:
        """Ad hoc DAO dependency overridde"""
        return first_part_fixture.ghga_secrets_dao_fixture.dao

    app.dependency_overrides[dao_injector] = dao_override

    payload = first_part_fixture.content

    request_body = {
        "user_id": "Test-User",
        "file_part": base64.b64encode(payload).hex(),
    }
    response = client.post(url="/secrets", json=request_body)
    assert response.status_code == 200
    body = response.json()
    secret = base64.b64decode(codecs.decode(body["secret"], "hex"))
    assert secret
    assert body["secret_id"]
    assert body["offset"] > 0


@pytest.mark.asyncio
async def test_corrupted_header(
    *,
    first_part_fixture: FirstPartFixture,  # noqa: F811
):
    """Test request response for /secrets endpoint with first char replaced in envelope"""

    async def dao_override() -> MongoDbDao:
        """Ad hoc DAO dependency overridde"""
        return first_part_fixture.ghga_secrets_dao_fixture.dao

    app.dependency_overrides[dao_injector] = dao_override

    payload = b"k" + first_part_fixture.content[2:]
    content = base64.b64encode(payload).hex()

    request_body = {
        "user_id": "Test-User",
        "file_part": content,
    }
    response = client.post(url="/secrets", json=request_body)
    assert response.status_code == 400
    body = response.json()
    assert body["exception_id"] == "malformedOrMissingEnvelopeError"


@pytest.mark.asyncio
async def test_missing_envelope(
    *,
    first_part_fixture: FirstPartFixture,  # noqa: F811
):
    """Test request response for /secrets endpoint without envelope"""

    async def dao_override() -> MongoDbDao:
        """Ad hoc DAO dependency overridde"""
        return first_part_fixture.ghga_secrets_dao_fixture.dao

    app.dependency_overrides[dao_injector] = dao_override

    payload = first_part_fixture.content
    content = base64.b64encode(payload).hex()
    content = content[124:]

    request_body = {
        "user_id": "Test-User",
        "file_part": content,
    }
    response = client.post(url="/secrets", json=request_body)
    assert response.status_code == 400
    body = response.json()
    assert body["exception_id"] == "malformedOrMissingEnvelopeError"


@pytest.mark.asyncio
async def test_invalid_secret(
    *,
    first_part_fixture: FirstPartFixture,  # noqa: F811
):
    """Test request response for"""

    async def dao_override() -> MongoDbDao:
        """Ad hoc DAO dependency overridde. Replace secret after encyption"""
        dao = first_part_fixture.ghga_secrets_dao_fixture.dao
        secret_id = first_part_fixture.ghga_secrets_dao_fixture.secret_id
        ghga_dao = await dao.get_ghga_secret_dao()
        await ghga_dao.delete(id_=secret_id)
        fake_secret = base64.b64encode(os.urandom(32)).hex()
        dto = GHGASecretCreationDto(
            public_key=fake_secret[::-1], private_key=fake_secret
        )
        await ghga_dao.insert(dto=dto)
        return dao

    app.dependency_overrides[dao_injector] = dao_override

    request_body = {
        "user_id": "Test-User",
        "file_part": base64.b64encode(first_part_fixture.content).hex(),
    }
    response = client.post(url="/secrets", json=request_body)
    assert response.status_code == 403
    body = response.json()
    assert body["exception_id"] == "envelopeDecryptionError"
