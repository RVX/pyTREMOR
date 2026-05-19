"""
Generate a high-quality dark-themed spectrogram preview for pyTREMOR README.
Fetches recent broadband data from SNZO (Wellington, NZ) via EarthScope.
Output: docs/pyTREMOR_output.png
"""

import datetime
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.collections import LineCollection
from matplotlib.ticker import MultipleLocator
from scipy.interpolate import interp1d as _interp1d
from obspy.clients.fdsn.routing.routing_client import RoutingClient

# --- Config ---
NETWORK      = "IU"
STATION      = "SNZO"
CHANNEL      = "BHZ"
LOCATION     = "*"
HOURS        = 2
FREQMIN      = 1.0
FREQMAX      = 19.0
SPEED_UP     = 200          # sonification speed-up factor (for MP4 label)
STATION_LOC  = "Wellington, New Zealand  |  41.31°S  174.70°E"
DB_MIN       = None  # auto-scaled from data
DB_MAX       = None  # auto-scaled from data
OUT_PATH     = "docs/pyTREMOR_output.png"

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

print(f"Fetching {STATION} {t1} -> {t2} ...")
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
# Two-column GridSpec: col 0 = data panels (waveform + spectrogram), col 1 = colorbar.
# This ensures ax_wave and ax_spec have identical pixel widths (sharex alone does
# not guarantee alignment when fig.colorbar steals space from only one panel).
gs  = gridspec.GridSpec(3, 2, figure=fig, hspace=0.06,
                        width_ratios=[40, 1], wspace=0.02,
                        top=0.88, bottom=0.10, left=0.07, right=0.97)

ax_wave = fig.add_subplot(gs[0, 0])
ax_spec = fig.add_subplot(gs[1:, 0], sharex=ax_wave)
cax     = fig.add_subplot(gs[1:, 1])  # dedicated colorbar axes

for ax in (ax_wave, ax_spec):
    ax.set_facecolor(BG)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_C)

# --- Waveform: frequency-coloured via spectral centroid ---
# First compute spectrogram to get centroid (reused for spectrogram panel too)
from scipy.signal import spectrogram as _sg
import warnings
nfft    = 512
overlap = int(nfft * 0.9)
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    f_sg, t_sg, Sxx = _sg(tr.data, fs=tr.stats.sampling_rate,
                          nperseg=nfft, noverlap=overlap, scaling="density")

centroid = np.sum(f_sg[:, None] * Sxx, axis=0) / (np.sum(Sxx, axis=0) + 1e-30)
t_abs_sg  = tr.stats.starttime.timestamp + t_sg
t_abs_tr  = tr.stats.starttime.timestamp + times_rel
centroid_per_sample = _interp1d(
    t_abs_sg, centroid, bounds_error=False, fill_value='extrapolate'
)(t_abs_tr)
centroid_norm = np.clip(
    (centroid_per_sample - FREQMIN) / (FREQMAX - FREQMIN + 1e-30), 0, 1
)
pts  = np.array([times_rel, tr.data]).T.reshape(-1, 1, 2)
segs = np.concatenate([pts[:-1], pts[1:]], axis=1)
lc   = LineCollection(segs, cmap='plasma', linewidth=0.5, alpha=0.9)
lc.set_array(centroid_norm[:-1])
ax_wave.add_collection(lc)

# RMS envelope
rms_win  = max(1, int(tr.stats.sampling_rate * 30))
rms_data = np.sqrt(np.convolve(tr.data**2, np.ones(rms_win)/rms_win, mode='same'))
ax_wave.fill_between(times_rel,  rms_data, alpha=0.18, color='#f0883e', linewidth=0)
ax_wave.fill_between(times_rel, -rms_data, alpha=0.18, color='#f0883e', linewidth=0)

ax_wave.set_ylabel("Amplitude\n(counts)", color=FG, fontsize=10)
ax_wave.tick_params(colors=FG, labelsize=9, which="both")
ax_wave.yaxis.label.set_color(FG)
max_amp = np.abs(tr.data).max()
ax_wave.set_xlim(times_rel[0], times_rel[-1])
ax_wave.set_ylim(-max_amp, max_amp)
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
# Use the same scipy arrays already computed for the centroid so that
# pcolormesh and the dominant-frequency ridge share identical time coordinates.
freq_mask = (f_sg >= FREQMIN) & (f_sg <= FREQMAX)
f_plot  = f_sg[freq_mask]
with np.errstate(divide="ignore", invalid="ignore"):
    Sxx_db = 10 * np.log10(Sxx[freq_mask] + 1e-30)  # (n_freq_plot, n_times)

vmin_auto = float(np.percentile(Sxx_db, 5))
vmax_auto = float(np.percentile(Sxx_db, 99))
print(f"  dB range: {vmin_auto:.1f} -> {vmax_auto:.1f}")

from matplotlib.colors import Normalize
norm = Normalize(vmin=vmin_auto, vmax=vmax_auto)
im = ax_spec.pcolormesh(
    t_sg, f_plot, Sxx_db,
    cmap="inferno", norm=norm, shading="nearest", rasterized=True
)

ax_spec.set_ylim(FREQMIN, FREQMAX)

# --- Dominant frequency ridge ---
# Restrict search to the displayed frequency band.
dom_idx  = np.argmax(Sxx[freq_mask], axis=0)  # index within f_plot
dom_freq = f_plot[dom_idx]
ax_spec.plot(t_sg, dom_freq, color='#e6edf3', linewidth=0.8, alpha=0.5,
             linestyle='--')
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

# colourbar — placed in the dedicated cax, never touching ax_wave
cbar = fig.colorbar(im, cax=cax)
cbar.set_label("Power (dB rel. 1 count\u00b2/Hz)", color=FG, fontsize=9)
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
         f"{STATION_LOC}  ·  bandpass {FREQMIN}–{FREQMAX} Hz"
         f"  ·  dB {vmin_auto:.0f}–{vmax_auto:.0f}  ·  {HOURS}h window  ·  {SPEED_UP}× speed-up (MP4)",
         color="#8b949e", fontsize=10, va="bottom")
fig.text(0.97, 0.905,
         "victormazon.com  ·  pyTREMOR v0.5",
         color="#8b949e", fontsize=9, ha="right", va="bottom")

plt.savefig(OUT_PATH, dpi=150, facecolor=BG, bbox_inches="tight")
print(f"Saved -> {OUT_PATH}")
