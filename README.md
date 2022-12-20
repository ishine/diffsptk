diffsptk
========
*diffsptk* is a differentiable version of [SPTK](https://github.com/sp-nitech/SPTK) based on the PyTorch framework.

[![Latest Manual](https://img.shields.io/badge/docs-latest-blue.svg)](https://sp-nitech.github.io/diffsptk/latest/)
[![Stable Manual](https://img.shields.io/badge/docs-stable-blue.svg)](https://sp-nitech.github.io/diffsptk/0.5.0/)
[![Python Version](https://img.shields.io/pypi/pyversions/diffsptk.svg)](https://pypi.python.org/pypi/diffsptk)
[![PyTorch Version](https://img.shields.io/badge/pytorch-1.10.0%20%7C%201.13.0-orange.svg)](https://pypi.python.org/pypi/diffsptk)
[![PyPI Version](https://img.shields.io/pypi/v/diffsptk.svg)](https://pypi.python.org/pypi/diffsptk)
[![Codecov](https://codecov.io/gh/sp-nitech/diffsptk/branch/master/graph/badge.svg)](https://app.codecov.io/gh/sp-nitech/diffsptk)
[![License](https://img.shields.io/github/license/sp-nitech/diffsptk.svg)](https://github.com/sp-nitech/diffsptk/blob/master/LICENSE)
[![GitHub Actions](https://github.com/sp-nitech/diffsptk/workflows/package/badge.svg)](https://github.com/sp-nitech/diffsptk/actions)


Requirements
------------
- Python 3.8+
- PyTorch 1.10.0+


Documentation
-------------
See [this page](https://sp-nitech.github.io/diffsptk/latest/) for a reference manual.


Installation
------------
The latest stable release can be installed through PyPI by running
```sh
pip install diffsptk
```
Alternatively,
```sh
git clone https://github.com/sp-nitech/diffsptk.git
pip install -e diffsptk
```


Examples
--------
### Mel-cepstral analysis and synthesis
```python
import diffsptk

# Set analysis condition.
fl = 400
fp = 80
n_fft = 512
M = 24

# Read waveform.
x, sr = diffsptk.read("assets/data.wav")

# Compute STFT amplitude of x.
stft = diffsptk.STFT(frame_length=fl, frame_period=fp, fft_length=n_fft)
X = stft(x)

# Estimate mel-cepstrum of x.
alpha = diffsptk.get_alpha(sr)
mcep = diffsptk.MelCepstralAnalysis(cep_order=M, fft_length=n_fft, alpha=alpha, n_iter=10)
mc = mcep(X)

# Reconstruct x.
mlsa = diffsptk.MLSA(filter_order=M, alpha=alpha, frame_period=fp, taylor_order=30)
x_hat = mlsa(mlsa(x, -mc), mc)

# Write reconstructed waveform.
diffsptk.write("reconst.wav", x_hat, sr)

# Compute error.
error = (x_hat - x).abs().sum()
print(error)

# Extract pitch of x.
pitch = diffsptk.Pitch(frame_period=fp, sample_rate=sr, f_min=80, f_max=180)
p = pitch(x)

# Generate excitation signal.
excite = diffsptk.ExcitationGeneration(frame_period=fp)
e = excite(p)
n = diffsptk.nrand(x.size(0) - 1)

# Synthesize waveform.
x_voiced = mlsa(e, mc)
x_unvoiced = mlsa(n, mc)

# Output analysis-synthesis result.
diffsptk.write("voiced.wav", x_voiced, sr)
diffsptk.write("unvoiced.wav", x_unvoiced, sr)
```

### Mel-spectrogram and MFCC extraction
```python
import diffsptk

# Set analysis condition.
fl = 400
fp = 80
n_fft = 512
n_channel = 80
M = 12

# Read waveform.
x, sr = diffsptk.read("assets/data.wav")

# Compute STFT amplitude of x.
stft = diffsptk.STFT(frame_length=fl, frame_period=fp, fft_length=n_fft)
X = stft(x)

# Extract mel-spectrogram.
fbank = diffsptk.MelFilterBankAnalysis(
    n_channel=n_channel,
    fft_length=n_fft,
    sample_rate=sr,
)
Y = fbank(X)
print(Y.shape)

# Extract MFCC.
mfcc = diffsptk.MFCC(
    mfcc_order=M,
    n_channel=n_channel,
    fft_length=n_fft,
    sample_rate=sr,
)
Y = mfcc(X)
print(Y.shape)
```

### Subband decomposition
```python
import diffsptk

K = 4   # Number of subbands.
M = 40  # Order of filter.

# Read waveform.
x, sr = diffsptk.read("assets/data.wav")

# Decompose x.
pqmf = diffsptk.PQMF(K, M)
decimate = diffsptk.Decimation(K)
y = decimate(pqmf(x), dim=-1)

# Reconstruct x.
interpolate = diffsptk.Interpolation(K)
ipqmf = diffsptk.IPQMF(K, M)
x_hat = ipqmf(interpolate(K * y, dim=-1)).reshape(-1)

# Write reconstructed waveform.
diffsptk.write("reconst.wav", x_hat, sr)

# Compute error.
error = (x_hat - x).abs().sum()
print(error)
```


License
-------
This software is released under the Apache License 2.0.
