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
"""Contains routes and associated data for the upload path"""

import base64
import codecs

from fastapi import APIRouter, Depends, status

from ekss.api.download import exceptions, models
from ekss.config import CONFIG
from ekss.core.dao.mongo_db import FileSecretDao
from ekss.core.envelope_encryption import get_envelope

download_router = APIRouter()

ERROR_RESPONSES = {
    "secretNotFoundError": {
        "description": (""),
        "model": exceptions.HttpSecretNotFoundError.get_body_model(),
    },
}


async def dao_injector() -> FileSecretDao:
    """Define dao as dependency to override during testing"""
    return FileSecretDao(config=CONFIG)


@download_router.get(
    "/secrets/{secret_id}/envelopes/{client_pk}",
    summary="Get personalized envelope containing Crypt4GH file encryption/decryption key",
    operation_id="getEncryptionData",
    status_code=status.HTTP_200_OK,
    response_model=models.OutboundEnvelopeContent,
    response_description="",
    responses={
        status.HTTP_404_NOT_FOUND: ERROR_RESPONSES["secretNotFoundError"],
    },
)
async def get_header_envelope(
    *,
    secret_id: str,
    client_pk: str,
    dao: FileSecretDao = Depends(dao_injector),
):
    """Create header envelope for the file secret with given ID encrypted with a given public key"""
    # Mypy false positives
    client_pubkey = base64.b64decode(
        codecs.decode(client_pk, "hex"),
    )

    file_secret = await dao.get_file_secret(id_=secret_id)

    if not file_secret:
        raise exceptions.HttpSecretNotFoundError()

    header_envelope = await (
        get_envelope(file_secret=file_secret, client_pubkey=client_pubkey)
    )

    return {
        "header_envelope": header_envelope,
    }
