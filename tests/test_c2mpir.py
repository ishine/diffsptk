# ------------------------------------------------------------------------ #
# Copyright 2022 SPTK Working Group                                        #
#                                                                          #
# Licensed under the Apache License, Version 2.0 (the "License");          #
# you may not use this file except in compliance with the License.         #
# You may obtain a copy of the License at                                  #
#                                                                          #
#     http://www.apache.org/licenses/LICENSE-2.0                           #
#                                                                          #
# Unless required by applicable law or agreed to in writing, software      #
# distributed under the License is distributed on an "AS IS" BASIS,        #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. #
# See the License for the specific language governing permissions and      #
# limitations under the License.                                           #
# ------------------------------------------------------------------------ #

import pytest

import diffsptk
import tests.utils as U


@pytest.mark.parametrize("device", ["cpu", "cuda"])
def test_compatibility(device, M=19, N=30, B=2):
    c2mpir = diffsptk.CepstrumToImpulseResponse(M, N)

    U.check_compatibility(
        device,
        c2mpir,
        [],
        f"nrand -l {B*(M+1)}",
        f"c2mpir -m {M} -l {N}",
        [],
        dx=M + 1,
        dy=N,
    )

    U.check_differentiable(device, c2mpir, [B, M + 1])
