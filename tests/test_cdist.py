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
import torch

import diffsptk
import tests.utils as U


@pytest.mark.parametrize("device", ["cpu", "cuda"])
@pytest.mark.parametrize("reduction", ["none", "batchmean"])
def test_compatibility(device, reduction, M=19, B=2):
    if device == "cuda" and not torch.cuda.is_available():
        return

    tmp1 = "cdist.tmp1"
    tmp2 = "cdist.tmp2"
    U.call(f"nrand -s 1 -l {B*(M+1)} > {tmp1}", get=False)
    U.call(f"nrand -s 2 -l {B*(M+1)} > {tmp2}", get=False)

    cdist = diffsptk.CepstralDistance(full=True, reduction=reduction).to(device)
    x1 = torch.from_numpy(U.call(f"cat {tmp1}").reshape(-1, M + 1)).to(device)
    x2 = torch.from_numpy(U.call(f"cat {tmp2}").reshape(-1, M + 1)).to(device)

    opt = "-f" if reduction == "none" else ""
    y = U.call(f"cdist {opt} -m {M} {tmp1} {tmp2}")
    U.call(f"rm {tmp1} {tmp2}", get=False)
    U.check_compatibility(y, cdist, x1, x2)


@pytest.mark.parametrize("device", ["cpu", "cuda"])
def test_differentiable(device, M=19, B=2):
    if device == "cuda" and not torch.cuda.is_available():
        return

    cdist = diffsptk.CepstralDistance().to(device)
    x1 = torch.randn(B, M + 1, requires_grad=True, device=device)
    x2 = torch.randn(B, M + 1, requires_grad=False, device=device)
    U.check_differentiable(cdist, x1, x2)
