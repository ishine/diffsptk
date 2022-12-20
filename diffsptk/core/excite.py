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

import torch
import torch.nn as nn

from ..misc.utils import is_in
from .linear_intpl import LinearInterpolation


class ExcitationGeneration(nn.Module):
    """See `this page <https://sp-nitech.github.io/sptk/latest/main/excite.html>`_
    for details.

    Parameters
    ----------
    frame_period : int >= 1 [scalar]
        Frame period in samples, :math:`P`.

    voiced_region : ['pulse', 'sinusoidal']
        Value on voiced region.

    unvoiced_region : ['gauss', 'zeros']
        Value on unvoiced region.

    """

    def __init__(self, frame_period, voiced_region="pulse", unvoiced_region="gauss"):
        super(ExcitationGeneration, self).__init__()

        self.frame_period = frame_period
        self.voiced_region = voiced_region
        self.unvoiced_region = unvoiced_region

        assert 1 <= self.frame_period
        assert is_in(self.voiced_region, ["pulse", "sinusoidal"])
        assert is_in(self.unvoiced_region, ["gauss", "zeros"])

        self.linear_intpl = LinearInterpolation(self.frame_period)

    def forward(self, p):
        """Generate a simple excitation signal.

        Parameters
        ----------
        p : Tensor [shape=(..., N)]
            Pitch in seconds.

        Returns
        -------
        e : Tensor [shape=(..., NxP)]
            Excitation signal.

        Examples
        --------
        >>> p = torch.tensor([2.0, 3.0])
        >>> excite = diffsptk.ExcitationGeneration(3)
        >>> e = excite(p)
        >>> e
        tensor([1.4142, 0.0000, 1.6330, 0.0000, 0.0000, 1.7321])

        """
        # Make mask represents voiced region.
        base_mask = torch.clip(p, min=0, max=1)

        signal_shape = list(base_mask.shape)
        signal_shape[-1] *= self.frame_period

        mask = torch.ne(base_mask, 0).unsqueeze(-1)
        size = [-1] * mask.dim()
        size[-1] = self.frame_period
        mask = mask.expand(size)
        mask = mask.reshape(signal_shape)

        # Extend right side for interpolation.
        tmp_mask = torch.cat((base_mask[..., :1] * 0, base_mask), dim=-1)
        tmp_mask = torch.eq(tmp_mask[..., 1:] - tmp_mask[..., :-1], -1)
        p[tmp_mask] = torch.roll(p, 1, dims=-1)[tmp_mask]

        # Interpolate pitch.
        d = p.dim()
        if d == 2 or d == 3:
            p = p.transpose(-1, -2)
        p = self.linear_intpl(p)
        if d == 2 or d == 3:
            p = p.transpose(-1, -2)
        p *= mask

        # Compute phase.
        q = torch.nan_to_num(torch.reciprocal(p), posinf=0)
        s = torch.cumsum(q.double(), dim=-1)
        bias, _ = torch.cummax(s * ~mask, dim=-1)
        phase = (s - bias).to(p.dtype)

        if self.voiced_region == "pulse":
            r = torch.ceil(phase)
            r = torch.cat((r[..., :1] * 0, r), dim=-1)
            pulse_pos = torch.ge(r[..., 1:] - r[..., :-1], 1)
            e = torch.zeros(*signal_shape, device=p.device, requires_grad=False)
            e[pulse_pos] = torch.sqrt(p[pulse_pos])
        elif self.voiced_region == "sinusoidal":
            e = torch.sin((2 * torch.pi) * phase)
        else:
            raise NotImplementedError

        if self.unvoiced_region == "gauss":
            e[~mask] = torch.randn(torch.sum(~mask), device=e.device)
        elif self.unvoiced_region == "zeros":
            pass
        else:
            raise NotImplementedError

        return e