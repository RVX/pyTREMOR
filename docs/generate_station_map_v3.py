#!/usr/bin/env python3
"""
pyTREMOR — Station Map Generator v3 (Gauss-Krüger / Transverse Mercator)
Three-strip GK projection: Europe/Africa | Asia/Pacific | Americas
by Victor Mazon Gardoqui — Kräken.LABS — root /at/ victormazon.com

GK/TM is designed for meridional strips; a three-strip layout covers the whole
globe without unbounded distortion at the edges.
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

# ── Hobart, Tasmania — base reference ──────────────────────────────────────────
TAS_LAT, TAS_LON = -42.8821, 147.3272

# ── Station data ────────────────────────────────────────────────────────────────
# (label, lat, true_lon, region, network, notes)
_STATIONS_RAW = [
    # EUROPE
    ("CEL\nEtna",        38.26,  15.89, "Europe",    "MN", "Mt. Etna / active"),
    ("OEM9\nN.Italy",    45.96,  11.23, "Europe",    "3D", "N. Italy / induced"),
    ("CURIE\nFrance",    48.00,   5.50, "Europe",    "FR", "France broadband"),
    ("BORG\nIceland",    64.75, -21.33, "Europe",    "II", "Litli-Hrútur / active"),
    # AMERICAS
    ("ILSW\nAlaska",     59.38,-153.49, "Americas",  "AV", "Iliamna / active"),
    ("RUS\nColombia",     5.89, -73.08, "Americas",  "CM", "Cordillera Oriental"),
    ("HEL\nRuiz",         6.19, -75.53, "Americas",  "CM", "Nevado del Ruiz"),
    # AFRICA
    ("DESE\nErta Ale",   11.12,  39.63, "Africa",    "AF", "Erta Ale / active"),
    # OCEANIA
    ("SNZO\nNew Zeal.", -41.31, 174.70, "Oceania",   "IU", "GSN Wellington"),
    ("RABL\nRabaul",     -4.19, 152.16, "Oceania",   "AU", "Tavurvur caldera"),
    ("HNR\nSolomon Is.", -9.44, 159.95, "Oceania",   "IU", "Near Tinakula"),
    ("AFI\nSamoa",      -13.91,-171.78, "Oceania",   "IU", "Samoa hotspot"),
    # ASIA
    ("MAJO\nJapan",      36.55, 138.20, "Asia",      "IU", "Asama / Ontake"),
    ("PET\nKamchatka",   53.02, 158.65, "Asia",      "IU", "Klyuchevskoy"),
    ("DAV\nPhilippines",  7.07, 125.58, "Asia",      "IU", "Apo / Mindanao"),
    ("GUMO\nGuam",       13.59, 144.87, "Asia",      "IU", "Mariana Arc"),
    ("GSI\nSumatra",      1.30,  97.57, "Asia",      "GE", "Sinabung / Toba"),
    ("SMRI\nSindoro",    -7.05, 110.44, "Asia",      "GE", "Mt. Sindoro / Java"),
    ("JAGI\nBromo",      -8.47, 114.15, "Asia",      "GE", "Mt. Bromo / Semeru"),
    ("TATO\nTaiwan",     24.97, 121.50, "Asia",      "IU", "Tatun volcanic"),
    # AUSTRALIA
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
    "IU": "o", "AU": "s", "GE": "D", "MN": "P",
    "II": "h", "AV": "^", "CM": "v", "AF": "*",
    "FR": "X", "3D": "p",
}

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlam = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlam/2)**2
    return 2 * R * np.arcsin(np.sqrt(a))

STATIONS = sorted(_STATIONS_RAW,
                  key=lambda s: haversine(TAS_LAT, TAS_LON, s[1], s[2]))

# ── Gauss-Krüger (spherical Transverse Mercator) projection ────────────────────
def gk(lons, lats, lon0):
    """Vectorized spherical GK/TM projection. Returns (x, y) in radians.

    Snyder (1987), Map Projections — A Working Manual, p. 57:
      B  = cos(φ) · sin(Δλ)
      x  = atanh(B)           [= ½ ln((1+B)/(1−B))]
      y  = atan(tan(φ)/cos(Δλ))
    Both coordinates are in radians; multiply by R (Earth radius) for metres.
    Central meridian λ₀ maps to x=0; equator to y=0.
    Valid without distortion limit for |Δλ| < ~85°.
    """
    lons = np.atleast_1d(np.asarray(lons, float))
    lats = np.atleast_1d(np.asarray(lats, float))
    phi  = np.radians(lats)
    dlam = np.radians(lons - lon0)
    dlam = (dlam + np.pi) % (2 * np.pi) - np.pi   # normalise to (−π, π]
    B    = np.cos(phi) * np.sin(dlam)
    B    = np.clip(B, -0.99999, 0.99999)            # guard atanh singularity
    x    = np.arctanh(B)
    cos_dlam = np.cos(dlam)
    with np.errstate(divide='ignore', invalid='ignore'):
        y = np.arctan(np.tan(phi) / cos_dlam)
        y = np.where(np.isfinite(y), y, np.sign(lats) * np.pi / 2)
    return x, y

def _dlam(lon, lon0):
    """Signed angular distance from lon to lon0, normalised to (−180, 180]."""
    return ((lon - lon0 + 180) % 360) - 180

def _interp_lons(lon1, lon2, n):
    """Linearly interpolate n longitudes from lon1 to lon2 the short way round."""
    delta = lon2 - lon1
    if delta >  180: delta -= 360
    if delta < -180: delta += 360
    return lon1 + np.linspace(0, delta, n)

# ── Panel configuration ─────────────────────────────────────────────────────────
# Three GK strips that collectively cover all 22 stations.
# lon0  : central meridian for this GK strip
# x_lim : display range in radians (corresponds to longitude offsets from lon0)
# hobart: True if Hobart falls in this strip (draw connection lines here)
Y_LIM = (-1.35, 1.35)   # ≈ ±77° latitude in radians
PANELS_CFG = [
    {"lon0":   20, "x_lim": (-1.55, 1.30), "title": "Europe & Africa  ·  GK λ₀ = 20°E",       "hobart": False},
    {"lon0":  130, "x_lim": (-1.75, 1.75), "title": "Asia, Pacific & Australia  ·  GK λ₀ = 130°E", "hobart": True},
    {"lon0":  -90, "x_lim": (-1.35, 0.90), "title": "Americas  ·  GK λ₀ = 90°W",               "hobart": False},
]

# Assign each station to the panel where its |Δλ| is smallest
def _best_panel(lon):
    return min(range(len(PANELS_CFG)),
               key=lambda i: abs(_dlam(lon, PANELS_CFG[i]["lon0"])))

PANEL_STATIONS = [[] for _ in PANELS_CFG]
for _s in STATIONS:
    PANEL_STATIONS[_best_panel(_s[2])].append(_s)


# ── Panel drawing routine ───────────────────────────────────────────────────────
def draw_panel(ax, cfg, stations_here):
    lon0  = cfg["lon0"]
    x_lim = cfg["x_lim"]

    ax.set_facecolor("#161b22")
    ax.set_xlim(x_lim)
    ax.set_ylim(Y_LIM)
    ax.set_title(cfg["title"], color="white", fontsize=11, pad=7, fontweight="bold")
    ax.tick_params(colors="#666", labelsize=7)
    for sp in ax.spines.values():
        sp.set_edgecolor("#30363d")

    # ── Graticule ──
    # Parallels: curved horizontal lines in GK
    for lat_g in range(-80, 81, 20):
        lons_p = np.linspace(lon0 - 88, lon0 + 88, 400)
        xs, ys = gk(lons_p, np.full_like(lons_p, lat_g), lon0)
        ax.plot(xs, ys, color="#1d2b3a", lw=0.45, zorder=0)
    # Meridians: curved vertical lines in GK
    for lon_g in range(-180, 181, 30):
        if abs(_dlam(lon_g, lon0)) > 88:
            continue
        lats_m = np.linspace(-82, 82, 300)
        xs, ys = gk(np.full_like(lats_m, lon_g), lats_m, lon0)
        ax.plot(xs, ys, color="#1d2b3a", lw=0.45, zorder=0)

    # ── Continent outlines ──
    for poly_pts in _CONTINENTS:
        poly_lons = np.array([p[0] for p in poly_pts], float)
        poly_lats = np.array([p[1] for p in poly_pts], float)
        xs, ys = gk(poly_lons, poly_lats, lon0)
        # Mask vertices in the back hemisphere (|Δλ| > 87°) → NaN breaks the line
        dlam_arr = np.abs(np.array([_dlam(l, lon0) for l in poly_lons]))
        mask = dlam_arr > 87
        xs[mask] = np.nan
        ys[mask] = np.nan
        xs_c = np.append(xs, xs[0])
        ys_c = np.append(ys, ys[0])
        ax.plot(xs_c, ys_c, color="#4a6a4a", alpha=0.32, lw=0.8, zorder=1)
        # Fill only when all vertices are in the valid hemisphere
        if not np.any(mask):
            ax.fill(xs, ys, color="#2a3a2a", alpha=0.18, zorder=0)

    # ── Hobart star ──
    hx, hy = gk(TAS_LON, TAS_LAT, lon0)
    hx, hy = float(np.squeeze(hx)), float(np.squeeze(hy))
    hobart_visible = cfg["hobart"] and (x_lim[0] < hx < x_lim[1])
    if hobart_visible:
        ax.plot(hx, hy, "*", color="#FFD700", markersize=15, zorder=10,
                markeredgecolor="#0d1117", markeredgewidth=0.8)
        ax.annotate("Hobart, Tasmania",
                    (hx, hy), textcoords="offset points",
                    xytext=(8, -20), color="#FFD700", fontsize=8.5, fontweight="bold")

    # ── Stations ──
    for label, lat, lon, region, network, _ in stations_here:
        sx, sy = gk(lon, lat, lon0)
        sx, sy = float(np.squeeze(sx)), float(np.squeeze(sy))
        color  = REGION_COLORS[region]
        marker = NETWORK_MARKERS.get(network, "o")

        # Connection line to Hobart (only drawn in panel 2 where Hobart is visible)
        if hobart_visible:
            n = 60
            lons_l = _interp_lons(TAS_LON, lon, n)
            lats_l = np.linspace(TAS_LAT, lat, n)
            lxs, lys = gk(lons_l, lats_l, lon0)
            # Hide segments that cross the back-hemisphere boundary
            lxs[np.abs(lxs) > 3.0] = np.nan
            ax.plot(lxs, lys, color=color, alpha=0.22, lw=0.9, zorder=2)

        ax.plot(sx, sy, marker, color=color, markersize=11,
                markeredgecolor="#0d1117", markeredgewidth=0.8, zorder=5)
        short = label.split("\n")[0]
        ax.annotate(short, (sx, sy), textcoords="offset points",
                    xytext=(6, 5), color=color, fontsize=8.5,
                    fontweight="bold", zorder=6)

    # ── Axis tick labels ──
    # X-axis: at the equator, x = atanh(sin(Δλ)) → Δλ = arcsin(tanh(x))
    x_tick_vals = np.arange(np.ceil(x_lim[0] * 2) / 2, x_lim[1] + 0.01, 0.5)
    lon_labels = []
    for xt in x_tick_vals:
        lo = lon0 + np.degrees(np.arcsin(float(np.clip(np.tanh(xt), -1, 1))))
        lo = ((lo + 180) % 360) - 180
        lon_labels.append(f"{abs(lo):.0f}°{'E' if lo >= 0 else 'W'}")
    ax.set_xticks(x_tick_vals)
    ax.set_xticklabels(lon_labels, color="#888", fontsize=6.5, rotation=38, ha='right')

    # Y-axis: along central meridian, y = radians(lat) exactly
    y_tick_lats = range(-60, 61, 20)
    ax.set_yticks([np.radians(lg) for lg in y_tick_lats])
    ax.set_yticklabels([f"{abs(lg)}°{'S' if lg<0 else 'N'}"
                        for lg in y_tick_lats], color="#888", fontsize=6.5)

    return hobart_visible


# ── Figure layout ───────────────────────────────────────────────────────────────
# Panel widths are proportional to each panel's x-range so GK scale stays uniform
P_XSPANS = [sum(abs(c) for c in cfg["x_lim"]) for cfg in PANELS_CFG]
MAP_FRAC  = 0.63          # fraction of figure devoted to the three map panels
GAP       = 0.007
FIG_H, FIG_B = 0.88, 0.07
total_xspan = sum(P_XSPANS)
p_widths = [MAP_FRAC * s / total_xspan for s in P_XSPANS]

ax_lefts = [0.01]
for w in p_widths[:-1]:
    ax_lefts.append(ax_lefts[-1] + w + GAP)
tbl_left = ax_lefts[-1] + p_widths[-1] + GAP + 0.005
tbl_w    = 1.0 - tbl_left - 0.01

fig = plt.figure(figsize=(46, 22), facecolor="#0d1117")
fig.suptitle(
    "pyTREMOR — Seismic Station Network  (v3 · Gauss-Krüger / Transverse Mercator)\n"
    "Victor Mazon Gardoqui · Kräken.LABS",
    color="white", fontsize=17, y=0.987, fontweight="bold"
)

axes = []
for i, cfg in enumerate(PANELS_CFG):
    ax = fig.add_axes([ax_lefts[i], FIG_B, p_widths[i], FIG_H])
    axes.append(ax)

ax_tbl = fig.add_axes([tbl_left, FIG_B, tbl_w, FIG_H])

for ax, cfg, sts in zip(axes, PANELS_CFG, PANEL_STATIONS):
    draw_panel(ax, cfg, sts)

# ── Table (right panel) — identical to v2 ──────────────────────────────────────
ax_tbl.set_facecolor("#161b22")
ax_tbl.axis("off")
ax_tbl.set_title("Station Reference", color="white", fontsize=14, pad=10)

col_headers = ["Station", "Net", "Region / Volcano", "Coordinates", "km"]
col_x       = [0.00, 0.17, 0.27, 0.60, 0.92]
row_h  = 0.044
header_y = 0.97

for i, h in enumerate(col_headers):
    ax_tbl.text(col_x[i], header_y, h, color="#FFD700", fontsize=11.5,
                fontweight="bold", transform=ax_tbl.transAxes, va="top")
ax_tbl.plot([0, 1], [header_y - 0.011, header_y - 0.011],
            color="#30363d", lw=0.8, transform=ax_tbl.transAxes, clip_on=False)

for idx, (label, lat, lon, region, network, notes) in enumerate(STATIONS):
    y     = header_y - 0.025 - idx * row_h
    color = REGION_COLORS[region]
    dist  = int(haversine(TAS_LAT, TAS_LON, lat, lon))
    short = label.replace("\n", " ")

    if idx % 2 == 0:
        ax_tbl.add_patch(mpatches.FancyBboxPatch(
            (0, y - row_h * 0.75), 1, row_h * 0.92,
            boxstyle="square,pad=0", facecolor="#1c2128", edgecolor="none",
            transform=ax_tbl.transAxes, zorder=0))

    ax_tbl.text(col_x[0], y, short,     color=color,   fontsize=10.5,
                transform=ax_tbl.transAxes, va="top", fontweight="bold")
    ax_tbl.text(col_x[1], y, network,   color="#aaa",  fontsize=10.5,
                transform=ax_tbl.transAxes, va="top")
    ax_tbl.text(col_x[2], y, notes,     color="#ccc",  fontsize=10,
                transform=ax_tbl.transAxes, va="top")
    lat_str = (f"{abs(lat):.2f}°{'S' if lat<0 else 'N'}  "
               f"{abs(lon):.2f}°{'W' if lon<0 else 'E'}")
    ax_tbl.text(col_x[3], y, lat_str,   color="#7a9fc2", fontsize=10,
                transform=ax_tbl.transAxes, va="top")
    ax_tbl.text(col_x[4], y, f"{dist:,}", color="#888", fontsize=10.5,
                transform=ax_tbl.transAxes, va="top", ha="left")

# ── Shared legend on middle (Asia/Pacific) panel ────────────────────────────────
seen_regions = {}
for _, _, _, region, _, _ in STATIONS:
    if region not in seen_regions:
        seen_regions[region] = REGION_COLORS[region]

region_patches = [mpatches.Patch(color=c, label=r) for r, c in seen_regions.items()]
network_handles = [
    Line2D([0], [0], marker=m, color="w", markerfacecolor="#aaa",
           markersize=7, label=f"{n} network", linestyle="None")
    for n, m in NETWORK_MARKERS.items()
    if any(s[4] == n for s in STATIONS)
]
tas_handle = Line2D([0], [0], marker="*", color="w", markerfacecolor="#FFD700",
                    markersize=10, label="Hobart (base)", linestyle="None")

axes[1].legend(
    handles=region_patches + network_handles + [tas_handle],
    loc="lower left", fontsize=9, framealpha=0.35,
    facecolor="#0d1117", edgecolor="#30363d", labelcolor="white", ncol=2
)

# ── Save ────────────────────────────────────────────────────────────────────────
out_path = "docs/pyTREMOR_stations_v3.png"
plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="#0d1117")
print(f"[+] Saved: {out_path}")
print(f"    Panel 1 (Europe/Africa): {len(PANEL_STATIONS[0])} stations")
print(f"    Panel 2 (Asia/Pacific):  {len(PANEL_STATIONS[1])} stations  [incl. Hobart]")
print(f"    Panel 3 (Americas):      {len(PANEL_STATIONS[2])} stations")
