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
Module containing the main FastAPI router and (optionally) top-level API enpoints.
Additional endpoints might be structured in dedicated modules
(each of them having a sub-router).
"""

from fastapi import FastAPI
from ghga_service_chassis_lib.api import ApiConfigBase, configure_app

from ekss.api.download.router import download_router
from ekss.api.upload.router import upload_router


def setup_app(config: ApiConfigBase):
    """Configure and return app"""
    app = FastAPI()
    configure_app(app, config=config)

    app.include_router(upload_router)
    app.include_router(download_router)

    return app
