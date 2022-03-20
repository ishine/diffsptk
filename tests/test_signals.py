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

import numpy as np

import diffsptk.signal
from tests.utils import call


def test_impulse(m=5):
    y = diffsptk.signal.impulse(m)
    y_ = call(f"impulse -m {m}")
    assert np.allclose(y, y_)


def test_step(m=5, v=-1):
    y = diffsptk.signal.step(m, v)
    y_ = call(f"step -m {m} -v {v}")
    assert np.allclose(y, y_)


def test_ramp(s=5, e=3, t=-1):
    y = diffsptk.signal.ramp(s, e, t)
    y_ = call(f"ramp -s {s} -e {e} -t {t}")
    assert np.allclose(y, y_)
