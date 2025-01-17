# Copyright (C) 2021, 2022 Genome Research Ltd.
#
# Author: Kieron Taylor kt19@sanger.ac.uk
# Author: Marina Gourtovaia mg8@sanger.ac.uk
#
# This file is part of npg_porch
#
# npg_porch is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.

from pydantic import BaseModel, Field
from typing import Optional

class Pipeline(BaseModel):
    name: str = Field(
        None,
        title='Pipeline Name',
        description='A user-controlled name for the pipeline'
    )
    version: Optional[str] = 'latest'
    uri: Optional[str] = Field(
        None,
        title='URI',
        description='URI to bootstrap the pipeline code'
    )
