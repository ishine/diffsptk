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

import warnings

import torch
import torch.nn as nn

from ..misc.utils import check_size
from .lpc2par import LinearPredictiveCoefficientsToParcorCoefficients
from .par2lpc import ParcorCoefficientsToLinearPredictiveCoefficients


class LinearPredictiveCoefficientsStabilityCheck(nn.Module):
    """See `this page <https://sp-nitech.github.io/sptk/latest/main/lpccheck.html>`_
    for details.

    Parameters
    ----------
    lpc_order : int >= 0
        Order of LPC, :math:`M`.

    margin : float in (0, 1)
        Margin for stability.

    warn_type : ['ignore', 'warn', 'exit']
        Warning type.

    """

    def __init__(self, lpc_order, margin=1e-16, warn_type="warn"):
        super(LinearPredictiveCoefficientsStabilityCheck, self).__init__()

        assert 0 < margin < 1

        self.lpc_order = lpc_order
        self.margin = margin
        self.warn_type = warn_type

    def forward(self, a):
        """Check stability of LPC.

        Parameters
        ----------
        a : Tensor [shape=(..., M+1)]
            LPC coefficients.

        Returns
        -------
        Tensor [shape=(..., M+1)]
            Modified LPC coefficients.

        Examples
        --------
        >>> x = diffsptk.nrand(4)
        tensor([-0.9966, -0.2970, -0.2173,  0.0594,  0.5831])
        >>> lpc = diffsptk.LPC(3, 5)
        >>> a = lpc(x)
        >>> a
        tensor([ 1.1528, -0.2613, -0.0274,  0.1778])
        >>> lpccheck = diffsptk.LinearPredictiveCoefficientsStabilityCheck(3)
        >>> a2 = lpccheck(a)
        tensor([ 1.1528, -0.2613, -0.0274,  0.1778])

        """
        check_size(a.size(-1), self.lpc_order + 1, "dimension of LPC")
        return self._forward(a, self.margin, self.warn_type)

    @staticmethod
    def _forward(a, margin, warn_type):
        k = LinearPredictiveCoefficientsToParcorCoefficients._func(a)
        K, k1 = torch.split(k, [1, k.size(-1) - 1], dim=-1)

        if torch.any(1 <= torch.abs(k1)):
            if warn_type == "ignore":
                pass
            elif warn_type == "warn":
                warnings.warn("Detected unstable LPC coefficients.")
            elif warn_type == "exit":
                raise RuntimeError("Detected unstable LPC coefficients.")
            else:
                raise RuntimeError

        bound = 1 - margin
        k1 = torch.clip(k1, -bound, bound)
        k2 = torch.cat((K, k1), dim=-1)
        a2 = ParcorCoefficientsToLinearPredictiveCoefficients._func(k2)
        return a2

    _func = _forward
