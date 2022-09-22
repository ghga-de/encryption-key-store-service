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
"""Implements functionality for envelope decryption and secret storage"""

import io
from typing import Tuple

import crypt4gh.header

from encryption_key_store.core.mongo_dao import (
    find_one_ghga_secret_key,
    insert_file_secret,
)


async def extract_envelope_content(
    *, file_part: bytes, ghga_secret: bytes
) -> Tuple[bytes, int]:
    """
    Extract file encryption/decryption secret and file content offset from envelope
    """
    envelope_stream = io.BytesIO(file_part)

    ghga_keys = [(0, ghga_secret, None)]
    session_keys, __ = crypt4gh.header.deconstruct(
        infile=envelope_stream,
        keys=ghga_keys,
    )

    file_secret = session_keys[0]
    offset = envelope_stream.tell()

    return file_secret, offset


async def store_secret(file_secret: bytes) -> str:
    """Store file secret, get id"""
    secret_id = await insert_file_secret(file_secret=file_secret)
    return secret_id


async def get_crypt4gh_private_key() -> bytes:
    """Retrieve current GHGA private key"""
    private_key = await find_one_ghga_secret_key()
    return private_key
