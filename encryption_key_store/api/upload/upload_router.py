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

from . import upload_exceptions, upload_models
from .envelope_decryption import extract_envelope_content, store_secret

router = APIRouter()

ERROR_RESPONSES = {
    "malformedOrMissingEnvelope": {
        "description": (""),
        "model": upload_exceptions.HttpMalformedOrMissingEnvelopeError.get_body_model(),
    },
    "envelopeDecryptionError": {
        "description": (""),
        "model": upload_exceptions.HttpEnvelopeDecrpytionError.get_body_model(),
    },
}


@router.post(
    "/envelopes",
    summary="Extract file encryption/decryption secret and file content offset from enevelope",
    operation_id="postEncryptionData",
    status_code=status.HTTP_200_OK,
    response_model=upload_models.InboundEnvelopeContent,
    response_description="",
    responses={
        status.HTTP_400_BAD_REQUEST: ERROR_RESPONSES["malformedOrMissingEnvelope"],
        status.HTTP_403_FORBIDDEN: ERROR_RESPONSES["envelopeDecryptionError"],
    },
)
async def post_encryption_secrets(
    *, envelope_query: upload_models.InboundEnvelopeQuery
):
    """Extract file encryption/decryption secret, create secret ID and extract
    file content offset"""
    user_id = envelope_query.user_id
    try:
        secret, offset = await extract_envelope_content(envelope_query.file_part)
    except ValueError as error:
        # Everything in crypt4gh is an ValueError... try to distinguish based on message
        if "No supported encryption method" == str(error):
            raise upload_exceptions.HttpEnvelopeDecrpytionError() from error
        raise upload_exceptions.HttpMalformedOrMissingEnvelopeError(
            user_id=user_id
        ) from error

    secret_id = await store_secret(secret)
    return {"secret": secret, "secret_id": secret_id, "offset": offset}
