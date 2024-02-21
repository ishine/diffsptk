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

import librosa
import numpy as np
import pytest
import torch

import diffsptk
import tests.utils as U


@pytest.mark.parametrize("device", ["cpu", "cuda"])
@pytest.mark.parametrize("scale", [False, True])
def test_compatibility(device, scale, n_bin=24, fp=512):
    if device == "cuda" and not torch.cuda.is_available():
        return

    x, sr = diffsptk.read(
        "assets/data.wav",
        double=torch.get_default_dtype() == torch.double,
        device=device,
    )

    c1 = librosa.cqt(
        x.cpu().numpy(),
        sr=sr,
        fmin=32.7,
        n_bins=n_bin,
        hop_length=fp,
        scale=scale,
        res_type="kaiser_best",
        dtype=None,
    ).T

    cqt = diffsptk.CQT(fp, sr, n_bin=n_bin, scale=scale).to(device)
    c2 = cqt(x).cpu().numpy()

    error = np.mean(np.abs(c1 - c2))
    assert error < 1e-4, f"Mean error: {error}"

    U.check_differentiability(device, [torch.abs, cqt], [fp])
