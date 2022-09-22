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

from fastapi import APIRouter, status

from encryption_key_store.api.upload import exceptions, models
from encryption_key_store.core.envelope_decryption import (
    extract_envelope_content,
    get_crypt4gh_private_key,
    insert_file_secret,
)

upload_router = APIRouter()

ERROR_RESPONSES = {
    "malformedOrMissingEnvelope": {
        "description": (""),
        "model": exceptions.HttpMalformedOrMissingEnvelopeError.get_body_model(),
    },
    "envelopeDecryptionError": {
        "description": (""),
        "model": exceptions.HttpEnvelopeDecrpytionError.get_body_model(),
    },
}


@upload_router.post(
    "/envelopes",
    summary="Extract file encryption/decryption secret and file content offset from enevelope",
    operation_id="postEncryptionData",
    status_code=status.HTTP_200_OK,
    response_model=models.InboundEnvelopeContent,
    response_description="",
    responses={
        status.HTTP_400_BAD_REQUEST: ERROR_RESPONSES["malformedOrMissingEnvelope"],
        status.HTTP_403_FORBIDDEN: ERROR_RESPONSES["envelopeDecryptionError"],
    },
)
async def post_encryption_secrets(*, envelope_query: models.InboundEnvelopeQuery):
    """Extract file encryption/decryption secret, create secret ID and extract
    file content offset"""
    user_id = envelope_query.user_id
    try:
        ghga_secret = await get_crypt4gh_private_key()
        file_secret, offset = await extract_envelope_content(
            file_part=envelope_query.file_part, ghga_secret=ghga_secret
        )
        secret_id = await insert_file_secret(file_secret=file_secret)
    except ValueError as error:
        # Everything in crypt4gh is an ValueError... try to distinguish based on message
        if "No supported encryption method" == str(error):
            raise exceptions.HttpEnvelopeDecrpytionError() from error
        raise exceptions.HttpMalformedOrMissingEnvelopeError(user_id=user_id) from error

    return {"secret": file_secret, "secret_id": secret_id, "offset": offset}
