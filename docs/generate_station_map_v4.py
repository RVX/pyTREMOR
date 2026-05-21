#!/usr/bin/env python3
"""
pyTREMOR — Station Map Generator v4 (Robinson Projection)
Single-panel world map with minimal distortion.  Familiar atlas look.
Central meridian 150°E keeps Hobart and the Pacific roughly centred.
by Victor Mazon Gardoqui — Kräken.LABS — root /at/ victormazon.com
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import numpy as np

# ── Continent outlines (lon, lat) — simplified polygons ────────────────────────
_CONTINENTS = [
    # Australia
    [(114,-22),(122,-18),(130,-12),(137,-13),(140,-17),(146,-19),(151,-24),(154,-28),
     (153,-32),(151,-34),(150,-38),(147,-39),(144,-38),(141,-36),(134,-33),(131,-32),
     (128,-34),(124,-34),(120,-34),(116,-32),(114,-28),(113,-25),(114,-22)],
    # New Zealand South Island
    [(166,-46),(168,-46),(170,-44),(172,-42),(172,-41),(170,-40),(168,-44),(166,-46)],
    # New Zealand North Island
    [(174,-41),(176,-40),(178,-38),(178,-37),(177,-38),(175,-40),(174,-41)],
    # Papua New Guinea
    [(131,-3),(135,-6),(140,-8),(145,-8),(148,-6),(150,-6),(152,-5),(150,-9),
     (145,-10),(141,-9),(138,-8),(134,-6),(131,-3)],
    # Indonesia (Sumatra + Java)
    [(96,5),(100,4),(104,1),(106,-2),(108,-7),(110,-8),(114,-8),(116,-8),(118,-9),
     (120,-10),(118,-9),(115,-8),(110,-7),(106,-6),(104,-4),(102,-2),(100,2),(98,3),(96,5)],
    # Philippines
    [(118,8),(120,10),(122,12),(124,12),(126,10),(124,8),(122,7),(120,8),(118,8)],
    # Japan (Honshu)
    [(130,31),(132,33),(135,34),(137,35),(138,36),(140,37),(141,38),(141,40),
     (140,42),(138,40),(136,37),(134,35),(132,33),(130,31)],
    # Taiwan
    [(120,22),(121,22),(122,23),(122,25),(121,25),(120,24),(120,22)],
    # Kamchatka
    [(158,52),(160,54),(162,55),(163,57),(162,58),(160,57),(158,55),(156,53),(158,52)],
    # Guam (tiny)
    [(144,13),(145,13),(145,14),(144,14),(144,13)],
    # Solomon Islands (tiny)
    [(159,-9),(162,-9),(162,-8),(159,-8),(159,-9)],
    # Macquarie Island (tiny)
    [(158,-54),(159,-54),(159,-55),(158,-55),(158,-54)],
    # Mainland Asia east coast
    [(100,0),(105,5),(108,15),(110,20),(115,25),(120,30),(122,32),(124,35),(126,38),
     (128,42),(130,45),(132,48),(135,50),(138,48),(135,45),(130,42),(128,38),(125,35),
     (122,30),(120,25),(115,20),(112,15),(108,10),(105,5),(100,0)],
    # Indian subcontinent
    [(62,22),(68,22),(72,20),(76,8),(80,8),(84,14),(80,14),(78,10),(76,8),(72,20),
     (68,22),(62,22)],
    # Europe (simplified)
    [(-10,36),(-10,44),(-6,44),(-2,48),(2,50),(4,52),(8,56),(10,58),(18,68),(28,72),
     (30,62),(28,56),(32,54),(28,48),(24,40),(20,38),(16,38),(14,40),(10,44),(8,44),
     (4,44),(2,44),(-2,46),(-5,44),(-8,44),(-10,36)],
    # Iceland
    [(-24,63),(-14,64),(-14,66),(-24,66),(-24,63)],
    # Africa (simplified)
    [(-18,16),(-14,10),(-10,5),(-2,4),(4,4),(8,4),(14,0),(18,-6),(22,-18),
     (26,-34),(32,-34),(38,-26),(40,-14),(44,2),(44,12),(44,22),(40,28),
     (36,32),(28,32),(22,28),(16,22),(10,14),(2,10),(-2,10),(-8,14),(-16,14),(-18,16)],
    # North America (simplified)
    [(-168,70),(-130,72),(-120,70),(-120,60),(-122,37),(-118,33),(-104,20),
     (-90,16),(-84,10),(-82,10),(-80,8),(-75,10),(-65,18),(-60,14),(-55,6),
     (-52,4),(-50,2),(-48,-2),(-42,-4),(-36,-8),(-36,-10),(-38,-14),(-40,-20),
     (-44,-28),(-48,-28),(-50,-30),(-52,-34),(-54,-42),(-60,-52),(-66,-56),
     (-68,-56),(-64,-42),(-66,-38),(-68,-32),(-70,-22),(-68,-10),(-68,-4),
     (-76,0),(-78,2),(-80,4),(-80,8),(-82,10),(-84,10),(-90,16),(-104,20),
     (-118,33),(-122,37),(-122,46),(-124,50),(-130,58),(-130,72),(-168,70)],
]

# ── Hobart & stations ───────────────────────────────────────────────────────────
TAS_LAT, TAS_LON = -42.8821, 147.3272

_STATIONS_RAW = [
    ("ANTO\nTurkey",     39.87,  32.79, "Europe",    "II", "Mediterranean arc / Aegean"),
    ("BFO\nGermany",     48.33,   8.33, "Europe",    "II", "C. Europe broadband"),
    ("CURIE\nFrance",    48.00,   5.50, "Europe",    "FR", "France broadband"),
    ("BORG\nIceland",    64.75, -21.33, "Europe",    "II", "Litli-Hrútur / active"),
    ("KDAK\nKodiak",     57.78,-152.58, "Americas",  "IU", "Kodiak Is. / Aleutian arc"),
    ("OTAV\nEcuador",     0.24, -78.45, "Americas",  "IU", "Cotopaxi / Pichincha"),
    ("NNA\nPeru",       -11.99, -76.84, "Americas",  "IU", "Andes volcanic arc"),
    ("ATD\nDjibouti",    11.53,  42.85, "Africa",    "II", "Afar Triangle / Erta Ale"),
    ("SNZO\nNew Zeal.", -41.31, 174.70, "Oceania",   "IU", "GSN Wellington"),
    ("RABL\nRabaul",     -4.19, 152.16, "Oceania",   "AU", "Tavurvur caldera"),
    ("HNR\nSolomon Is.", -9.44, 159.95, "Oceania",   "IU", "Near Tinakula"),
    ("AFI\nSamoa",      -13.91,-171.78, "Oceania",   "IU", "Samoa hotspot"),
    ("MAJO\nJapan",      36.55, 138.20, "Asia",      "IU", "Asama / Ontake"),
    ("MA2\nMagadan",     59.58, 150.77, "Asia",      "II", "Kamchatka / Klyuchevskoy"),
    ("DAV\nPhilippines",  7.07, 125.58, "Asia",      "IU", "Apo / Mindanao"),
    ("GUMO\nGuam",       13.59, 144.87, "Asia",      "IU", "Mariana Arc"),
    ("GSI\nSumatra",      1.30,  97.57, "Asia",      "GE", "Sinabung / Toba"),
    ("SMRI\nSindoro",    -7.05, 110.44, "Asia",      "GE", "Mt. Sindoro / Java"),
    ("JAGI\nBromo",      -8.47, 114.15, "Asia",      "GE", "Mt. Bromo / Semeru"),
    ("TATO\nTaiwan",     24.97, 121.50, "Asia",      "IU", "Tatun volcanic"),
    ("MCQ\nMacquarie",  -54.50, 158.94, "Australia", "AU", "Macquarie Ridge"),
    ("NWAO\nNarrogin",  -32.93, 117.24, "Australia", "IU", "Heard Is. proxy"),
]

REGION_COLORS = {
    "Europe":    "#FF9800",
    "Americas":  "#E91E63",
    "Africa":    "#9C27B0",
    "Oceania":   "#00BCD4",
    "Asia":      "#F44336",
    "Australia": "#4CAF50",
}
NETWORK_MARKERS = {
    "IU": "o", "AU": "s", "GE": "D",
    "II": "h", "FR": "X",
}

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    a = (np.sin(np.radians(lat2-lat1)/2)**2
         + np.cos(phi1)*np.cos(phi2)*np.sin(np.radians(lon2-lon1)/2)**2)
    return 2 * R * np.arcsin(np.sqrt(a))

STATIONS = sorted(_STATIONS_RAW,
                  key=lambda s: haversine(TAS_LAT, TAS_LON, s[1], s[2]))

# ── Robinson projection ─────────────────────────────────────────────────────────
# Piecewise lookup table (Snyder, 1988) at 5° latitude steps 0°→90°:
# PLEN = length of parallel relative to equator
# PDFE = distance from equator relative to pole–equator distance
_ROB_TABLE = [
    (1.0000, 0.0000), (0.9986, 0.0620), (0.9954, 0.1240), (0.9900, 0.1860),
    (0.9822, 0.2480), (0.9730, 0.3100), (0.9600, 0.3720), (0.9427, 0.4340),
    (0.9216, 0.4958), (0.8962, 0.5571), (0.8679, 0.6176), (0.8350, 0.6769),
    (0.7986, 0.7346), (0.7597, 0.7903), (0.7186, 0.8435), (0.6732, 0.8936),
    (0.6213, 0.9394), (0.5722, 0.9761), (0.5322, 1.0000),
]
_ROB_LATS = np.linspace(0.0, 90.0, 19)
_ROB_PLEN = np.array([t[0] for t in _ROB_TABLE])
_ROB_PDFE = np.array([t[1] for t in _ROB_TABLE])

# Central meridian: 150°E  (Pacific-centred, Hobart ~0° offset)
LON0 = 150.0

def robinson(lons_deg, lats_deg):
    """Vectorised Robinson projection → (x, y) unit-sphere coordinates.

    Natural extent: x ∈ [−2.667, +2.667],  y ∈ [−1.352, +1.352]
    Projection:
      x = 0.8487 · PLEN(|φ|) · Δλ   (Δλ in radians, normalised to (−π, π])
      y = 1.3523 · PDFE(|φ|) · sign(φ)
    """
    lons = np.atleast_1d(np.asarray(lons_deg, float))
    lats = np.atleast_1d(np.asarray(lats_deg, float))
    plen = np.interp(np.clip(np.abs(lats), 0, 90), _ROB_LATS, _ROB_PLEN)
    pdfe = np.interp(np.clip(np.abs(lats), 0, 90), _ROB_LATS, _ROB_PDFE)
    dlam = np.radians(lons - LON0)
    dlam = (dlam + np.pi) % (2 * np.pi) - np.pi   # wrap to (−π, π]
    x = 0.8487 * dlam * plen
    y = 1.3523 * pdfe * np.sign(lats + 1e-15)
    return x, y

def _interp_lons(lon1, lon2, n=80):
    """Interpolate n longitudes from lon1 to lon2 the short way round the globe."""
    delta = lon2 - lon1
    if delta >  180: delta -= 360
    if delta < -180: delta += 360
    return lon1 + np.linspace(0, delta, n)

# Natural map extent
_XMAX = 0.8487 * np.pi         # ≈ 2.666
_YMAX = 1.3523                 # pole y-coordinate

# ── Figure ──────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(50, 24), facecolor="#0d1117")
fig.suptitle(
    "pyTREMOR Seismic Station Network Map\n"
    "v0.4  ·  Robinson Projection\n"
    "by Víctor Mazón Gardoqui  ·  05-2026",
    color="#5BA8FF", fontsize=24, y=0.994, fontweight="bold", linespacing=1.5
)

ax_map = fig.add_axes([0.01, 0.04, 0.61, 0.88])
ax_tbl = fig.add_axes([0.64, 0.04, 0.35, 0.88])

ax_map.set_facecolor("#0d1117")      # figure background colour (outside oval)
ax_map.set_xlim(-_XMAX - 0.12, _XMAX + 0.35)
ax_map.set_ylim(-_YMAX - 0.45, _YMAX + 0.08)
ax_map.axis("off")

# ── Ocean fill: Robinson oval ────────────────────────────────────────────────────
lats_r = np.linspace(-90, 90, 500)
lats_l = np.linspace(90, -90, 500)
xs_r, ys_r = robinson(np.full(500, LON0 + 179.95), lats_r)
xs_l, ys_l = robinson(np.full(500, LON0 - 179.95), lats_l)
bx = np.concatenate([xs_r, xs_l])
by = np.concatenate([ys_r, ys_l])
ax_map.fill(bx, by, color="#161b22", zorder=0)                     # ocean
ax_map.plot(np.append(bx, bx[0]), np.append(by, by[0]),
            color="#384454", lw=1.2, zorder=9)                     # border

# ── Graticule ────────────────────────────────────────────────────────────────────
# Parallels — straight horizontal line segments in Robinson
for lat_g in range(-80, 81, 20):
    plen_g = float(np.interp(abs(lat_g), _ROB_LATS, _ROB_PLEN))
    pdfe_g = float(np.interp(abs(lat_g), _ROB_LATS, _ROB_PDFE))
    y_g    = 1.3523 * pdfe_g * (1 if lat_g >= 0 else -1)
    x_ext  = 0.8487 * np.pi * plen_g
    ax_map.plot([-x_ext, x_ext], [y_g, y_g], color="#1d2b3a", lw=0.50, zorder=1)

# Meridians — curved lines converging toward poles
for lon_off in range(-180, 181, 30):
    lon_g  = LON0 + lon_off
    lats_m = np.linspace(-88, 88, 400)
    xs, ys = robinson(np.full_like(lats_m, lon_g), lats_m)
    ax_map.plot(xs, ys, color="#1d2b3a", lw=0.50, zorder=1)

# ── Continent outlines ────────────────────────────────────────────────────────────
for poly_pts in _CONTINENTS:
    plons = np.array([p[0] for p in poly_pts], float)
    plats = np.array([p[1] for p in poly_pts], float)
    xs, ys = robinson(plons, plats)
    ax_map.fill(xs, ys, color="#2a3a2a", alpha=0.24, zorder=2)
    ax_map.plot(np.append(xs, xs[0]), np.append(ys, ys[0]),
                color="#4a6a4a", alpha=0.35, lw=0.8, zorder=2)

# ── Graticule labels ─────────────────────────────────────────────────────────────
# Longitude labels placed just below the southern map boundary
for lon_off in range(-180, 181, 30):
    lon_g = LON0 + lon_off
    lo = ((lon_g + 180) % 360) - 180          # canonical [-180, 180]
    xs_l, _ = robinson(lon_g, 0)
    label = "0°" if abs(lo) < 0.5 else f"{abs(lo):.0f}°{'E' if lo > 0 else 'W'}"
    ax_map.text(float(np.squeeze(xs_l)), -_YMAX - 0.08, label,
                color="#888", fontsize=11, ha="center", va="top", zorder=5)

# Latitude labels placed just beyond the right edge of each parallel
for lat_g in range(-80, 81, 20):
    plen_g = float(np.interp(abs(lat_g), _ROB_LATS, _ROB_PLEN))
    pdfe_g = float(np.interp(abs(lat_g), _ROB_LATS, _ROB_PDFE))
    y_g   = 1.3523 * pdfe_g * (1 if lat_g >= 0 else -1)
    x_r   = 0.8487 * np.pi * plen_g + 0.07
    label = f"{abs(lat_g)}°{'S' if lat_g < 0 else 'N'}"
    ax_map.text(x_r, y_g, label, color="#888", fontsize=11,
                ha="left", va="center", zorder=5)

# Bottom subtitle (below longitude labels)
ax_map.text(0, -_YMAX - 0.32,
            "Global Station Locations  —  Robinson Projection  (λ₀ = 150°E, Pacific-centred)",
            color="#5BA8FF", fontsize=14, ha="center", va="top",
            fontweight="bold", zorder=5)

# ── Hobart (base station) ────────────────────────────────────────────────────────
hx, hy = robinson(TAS_LON, TAS_LAT)
hx, hy = float(np.squeeze(hx)), float(np.squeeze(hy))
ax_map.plot(hx, hy, "*", color="#FFD700", markersize=18, zorder=11,
            markeredgecolor="#0d1117", markeredgewidth=0.8)
ax_map.annotate("Hobart, Tasmania\n42.88°S  147.33°E",
                (hx, hy), textcoords="offset points",
                xytext=(10, -34), color="#FFD700", fontsize=13, fontweight="bold",
                zorder=12)

# ── Stations: connection lines + markers + labels ────────────────────────────────
for label, lat, lon, region, network, _ in STATIONS:
    sx, sy = robinson(lon, lat)
    sx, sy = float(np.squeeze(sx)), float(np.squeeze(sy))
    color  = REGION_COLORS[region]
    marker = NETWORK_MARKERS.get(network, "o")

    # Great-circle approximation: linear interpolation in geo space → project
    lons_l = _interp_lons(TAS_LON, lon)
    lats_l = np.linspace(TAS_LAT, lat, 80)
    lxs, lys = robinson(lons_l, lats_l)
    # Detect seam jumps (shouldn't occur with lon0=150°E but guard anyway)
    dx = np.abs(np.diff(lxs))
    lxs[1:][dx > 1.2] = np.nan
    ax_map.plot(lxs, lys, color=color, alpha=0.22, lw=0.9, zorder=3)

    ax_map.plot(sx, sy, marker, color=color, markersize=13,
                markeredgecolor="#0d1117", markeredgewidth=0.8, zorder=7)
    short = label.split("\n")[0]
    ax_map.annotate(short, (sx, sy), textcoords="offset points",
                    xytext=(7, 6), color=color, fontsize=11,
                    fontweight="bold", zorder=8)

# ── Legend ────────────────────────────────────────────────────────────────────────
seen_regions = {}
for _, _, _, region, _, _ in STATIONS:
    if region not in seen_regions:
        seen_regions[region] = REGION_COLORS[region]
region_patches = [mpatches.Patch(color=c, label=r) for r, c in seen_regions.items()]
net_handles = [
    Line2D([0], [0], marker=m, color="w", markerfacecolor="#aaa",
           markersize=7, label=f"{n} network", linestyle="None")
    for n, m in NETWORK_MARKERS.items() if any(s[4] == n for s in STATIONS)
]
tas_handle = Line2D([0], [0], marker="*", color="w", markerfacecolor="#FFD700",
                    markersize=10, label="Hobart (base)", linestyle="None")
ax_map.legend(
    handles=region_patches + net_handles + [tas_handle],
    loc="lower left", fontsize=12, framealpha=0.45,
    facecolor="#0d1117", edgecolor="#30363d", labelcolor="white", ncol=2
)

# ── Table (right panel) ───────────────────────────────────────────────────────────
ax_tbl.set_facecolor("#161b22")
ax_tbl.axis("off")
ax_tbl.set_title("Station Reference", color="white", fontsize=18, pad=12)

col_headers = ["Station", "Net", "Region / Volcano", "Coordinates", "km"]
col_x       = [0.00, 0.17, 0.27, 0.60, 0.92]
row_h       = 0.044
header_y    = 0.96

for i, h in enumerate(col_headers):
    ax_tbl.text(col_x[i], header_y, h, color="#FFD700", fontsize=14,
                fontweight="bold", transform=ax_tbl.transAxes, va="top")
ax_tbl.plot([0, 1], [header_y - 0.012] * 2,
            color="#30363d", lw=1.0, transform=ax_tbl.transAxes, clip_on=False)

for idx, (label, lat, lon, region, network, notes) in enumerate(STATIONS):
    y     = header_y - 0.028 - idx * row_h
    color = REGION_COLORS[region]
    dist  = int(haversine(TAS_LAT, TAS_LON, lat, lon))
    short = label.replace("\n", " ")

    if idx % 2 == 0:
        ax_tbl.add_patch(mpatches.FancyBboxPatch(
            (0, y - row_h * 0.75), 1, row_h * 0.92,
            boxstyle="square,pad=0", facecolor="#1c2128", edgecolor="none",
            transform=ax_tbl.transAxes, zorder=0))

    ax_tbl.text(col_x[0], y, short,    color=color,    fontsize=13,
                transform=ax_tbl.transAxes, va="top", fontweight="bold")
    ax_tbl.text(col_x[1], y, network,  color="#aaa",   fontsize=13,
                transform=ax_tbl.transAxes, va="top")
    ax_tbl.text(col_x[2], y, notes,    color="#ccc",   fontsize=12,
                transform=ax_tbl.transAxes, va="top")
    lat_str = (f"{abs(lat):.2f}°{'S' if lat<0 else 'N'}  "
               f"{abs(lon):.2f}°{'W' if lon<0 else 'E'}")
    ax_tbl.text(col_x[3], y, lat_str,  color="#7a9fc2", fontsize=12,
                transform=ax_tbl.transAxes, va="top")
    ax_tbl.text(col_x[4], y, f"{dist:,}", color="#888", fontsize=13,
                transform=ax_tbl.transAxes, va="top", ha="left")

# ── Save ──────────────────────────────────────────────────────────────────────────
out_path = "docs/pyTREMOR_stations_v4.png"
plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="#0d1117")
print(f"[+] Saved: {out_path}")
print(f"    Projection: Robinson  (λ₀ = {LON0}°E)")
print(f"    Stations:   {len(STATIONS)}")
