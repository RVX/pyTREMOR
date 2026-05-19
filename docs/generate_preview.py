"""
Generate a high-quality dark-themed spectrogram preview for pyTREMOR README.
Fetches recent broadband data from SNZO (Wellington, NZ) via EarthScope.
Output: docs/pyTREMOR_preview.png
"""

import datetime
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import MultipleLocator
from obspy.clients.fdsn.routing.routing_client import RoutingClient

# --- Config ---
NETWORK  = "IU"
STATION  = "SNZO"
CHANNEL  = "BHZ"
LOCATION = "*"
HOURS    = 2
FREQMIN  = 1.0
FREQMAX  = 19.0
DB_MIN   = None  # auto-scaled from data
DB_MAX   = None  # auto-scaled from data
OUT_PATH = "docs/pyTREMOR_preview.png"

BG       = "#0d1117"
FG       = "#e6edf3"
ACCENT   = "#58a6ff"
GRID_C   = "#21262d"

# --- Fetch ---
endtime   = datetime.datetime.utcnow()
starttime = endtime - datetime.timedelta(hours=HOURS)

from obspy import UTCDateTime
t1 = UTCDateTime(starttime)
t2 = UTCDateTime(endtime)

print(f"Fetching {STATION} {t1} → {t2} ...")
client = RoutingClient("iris-federator")
st = client.get_waveforms(network=NETWORK, station=STATION, location=LOCATION,
                          channel=CHANNEL, starttime=t1, endtime=t2)
st.merge(fill_value="interpolate")
tr = st[0]
tr.detrend("demean")
tr.detrend("linear")
tr.taper(max_percentage=0.02)
tr.filter("bandpass", freqmin=FREQMIN, freqmax=FREQMAX, corners=4, zerophase=True)

print(f"  Got {tr.stats.npts} samples @ {tr.stats.sampling_rate} Hz")

# --- Times for x-axis ---
times_rel = tr.times()  # seconds from start
t_start_utc = tr.stats.starttime.datetime

# --- Figure ---
fig = plt.figure(figsize=(18, 9), facecolor=BG)
gs  = gridspec.GridSpec(3, 1, figure=fig, hspace=0.06,
                        top=0.88, bottom=0.10, left=0.07, right=0.97)

ax_wave = fig.add_subplot(gs[0])
ax_spec = fig.add_subplot(gs[1:], sharex=ax_wave)

for ax in (ax_wave, ax_spec):
    ax.set_facecolor(BG)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_C)

# --- Waveform ---
ax_wave.plot(times_rel, tr.data, color=ACCENT, linewidth=0.4, alpha=0.9)
ax_wave.set_ylabel("Amplitude\n(counts)", color=FG, fontsize=10)
ax_wave.tick_params(colors=FG, labelsize=9, which="both")
ax_wave.yaxis.label.set_color(FG)
ax_wave.set_xlim(times_rel[0], times_rel[-1])
ax_wave.axhline(0, color=GRID_C, linewidth=0.5)
ax_wave.grid(True, color=GRID_C, linewidth=0.4, linestyle="--", alpha=0.6)
ax_wave.xaxis.set_visible(False)

# peak annotation
peak_idx = np.argmax(np.abs(tr.data))
peak_t   = times_rel[peak_idx]
peak_v   = tr.data[peak_idx]
ax_wave.annotate(f"peak: {peak_v:.0f}", xy=(peak_t, peak_v),
                 xytext=(peak_t + times_rel[-1]*0.01, peak_v * 0.85),
                 color="#f0883e", fontsize=8.5,
                 arrowprops=dict(arrowstyle="->", color="#f0883e", lw=0.8))

# --- Spectrogram ---
from matplotlib.colors import Normalize
nfft    = 512
overlap = int(nfft * 0.9)

# Compute spectrogram power to auto-scale dB range
from scipy.signal import spectrogram as _sg
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    f_sg, t_sg, Sxx = _sg(tr.data, fs=tr.stats.sampling_rate,
                          nperseg=nfft, noverlap=overlap, scaling="density")
with np.errstate(divide="ignore"):
    Sxx_db = 10 * np.log10(np.abs(Sxx) + 1e-30)
freq_mask = (f_sg >= FREQMIN) & (f_sg <= FREQMAX)
valid = Sxx_db[freq_mask]
vmin_auto = float(np.percentile(valid, 5))
vmax_auto = float(np.percentile(valid, 99))
print(f"  dB range: {vmin_auto:.1f} → {vmax_auto:.1f}")

Pxx, freqs, bins, im = ax_spec.specgram(
    tr.data,
    NFFT=nfft,
    Fs=tr.stats.sampling_rate,
    noverlap=overlap,
    cmap="inferno",
    vmin=vmin_auto,
    vmax=vmax_auto,
    scale="dB",
    mode="psd",
)

# restrict y-axis to filter range
ax_spec.set_ylim(FREQMIN, FREQMAX)
ax_spec.set_ylabel("Frequency (Hz)", color=FG, fontsize=10)
ax_spec.tick_params(colors=FG, labelsize=9, which="both")
ax_spec.yaxis.label.set_color(FG)
ax_spec.grid(True, color=GRID_C, linewidth=0.3, linestyle="--", alpha=0.5)

# x-axis: UTC time labels
total_sec = times_rel[-1]
n_ticks   = 9
tick_locs = np.linspace(0, total_sec, n_ticks)
tick_lbls = [
    (t_start_utc + datetime.timedelta(seconds=float(s))).strftime("%H:%M")
    for s in tick_locs
]
ax_spec.set_xticks(tick_locs)
ax_spec.set_xticklabels(tick_lbls, color=FG, fontsize=9)
ax_spec.set_xlabel("UTC Time", color=FG, fontsize=10)

# colourbar
cbar = fig.colorbar(im, ax=ax_spec, pad=0.01, fraction=0.012)
cbar.set_label("Power (dB)", color=FG, fontsize=9)
cbar.ax.yaxis.set_tick_params(color=FG, labelsize=8)
plt.setp(cbar.ax.yaxis.get_ticklabels(), color=FG)
cbar.outline.set_edgecolor(GRID_C)

# --- Title & metadata ---
date_str  = t_start_utc.strftime("%Y-%m-%d")
range_str = (f"{t_start_utc.strftime('%H:%M')} – "
             f"{(t_start_utc + datetime.timedelta(hours=HOURS)).strftime('%H:%M')} UTC")

fig.text(0.07, 0.94,
         f"pyTREMOR  ·  {NETWORK}.{STATION}  ·  {CHANNEL}  ·  {date_str}  ·  {range_str}",
         color=FG, fontsize=13, fontweight="bold", va="bottom")
fig.text(0.07, 0.905,
         f"Wellington, New Zealand  ·  bandpass {FREQMIN}–{FREQMAX} Hz  ·  dB {vmin_auto:.0f}–{vmax_auto:.0f}  ·  {HOURS}h window",
         color="#8b949e", fontsize=10, va="bottom")
fig.text(0.97, 0.905,
         "victormazon.com  ·  pyTREMOR v0.5",
         color="#8b949e", fontsize=9, ha="right", va="bottom")

plt.savefig(OUT_PATH, dpi=150, facecolor=BG, bbox_inches="tight")
print(f"Saved → {OUT_PATH}")
