#!/usr/bin/env python3
"""
pyTREMOR — Station Map Generator v2 (Global)
Generates a visual chart of all configured seismic stations on a global map.
by Victor Mazon Gardoqui, supported by Kräken.LABS — root /at/ victormazon.com
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import numpy as np

# ── Continent outlines (lon, lat) — simplified polygons ────────────────────────
# Stations west of MAP_WEST are wrapped to lon+360; see display logic below.
# All coordinates in true lon (-180..180); wrapping applied at render time.
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

# ── Map display range ───────────────────────────────────────────────────────────
MAP_WEST, MAP_EAST = -115, 215   # longitude range (°)
# Stations whose true lon < MAP_WEST are wrapped to lon+360 for display
# (Alaska ~-153 → 207°, Samoa ~-172 → 188°)

# Hobart, Tasmania — base reference location
TAS_LAT, TAS_LON = -42.8821, 147.3272

# ── All stations from current autoconfig ────────────────────────────────────────
# (label, lat, true_lon, region, network, notes)
_STATIONS_RAW = [
    # EUROPE
    ("CEL\nEtna",       38.26,  15.89, "Europe",   "MN", "Mt. Etna / active"),
    ("OEM9\nN.Italy",   45.96,  11.23, "Europe",   "3D", "N. Italy / induced"),
    ("CURIE\nFrance",   48.00,   5.50, "Europe",   "FR", "France broadband"),
    ("BORG\nIceland",   64.75, -21.33, "Europe",   "II", "Litli-Hrútur / active"),
    # AMERICAS
    ("ILSW\nAlaska",    59.38,-153.49, "Americas", "AV", "Iliamna / active"),
    ("RUS\nColombia",    5.89, -73.08, "Americas", "CM", "Cordillera Oriental"),
    ("HEL\nRuiz",        6.19, -75.53, "Americas", "CM", "Nevado del Ruiz"),
    # AFRICA
    ("DESE\nErta Ale",  11.12,  39.63, "Africa",   "AF", "Erta Ale / active"),
    # OCEANIA
    ("SNZO\nNew Zeal.", -41.31, 174.70, "Oceania",  "IU", "GSN Wellington"),
    ("RABL\nRabaul",     -4.19, 152.16, "Oceania",  "AU", "Tavurvur caldera"),
    ("HNR\nSolomon Is.", -9.44, 159.95, "Oceania",  "IU", "Near Tinakula"),
    ("AFI\nSamoa",      -13.91,-171.78, "Oceania",  "IU", "Samoa hotspot"),
    # ASIA
    ("MAJO\nJapan",      36.55, 138.20, "Asia",     "IU", "Asama / Ontake"),
    ("PET\nKamchatka",   53.02, 158.65, "Asia",     "IU", "Klyuchevskoy"),
    ("DAV\nPhilippines",  7.07, 125.58, "Asia",     "IU", "Apo / Mindanao"),
    ("GUMO\nGuam",       13.59, 144.87, "Asia",     "IU", "Mariana Arc"),
    ("GSI\nSumatra",      1.30,  97.57, "Asia",     "GE", "Sinabung / Toba"),
    ("SMRI\nSindoro",    -7.05, 110.44, "Asia",     "GE", "Mt. Sindoro / Java"),
    ("JAGI\nBromo",      -8.47, 114.15, "Asia",     "GE", "Mt. Bromo / Semeru"),
    ("TATO\nTaiwan",     24.97, 121.50, "Asia",     "IU", "Tatun volcanic"),
    # AUSTRALIA
    ("MCQ\nMacquarie",  -54.50, 158.94, "Australia","AU", "Macquarie Ridge"),
    ("NWAO\nNarrogin",  -32.93, 117.24, "Australia","IU", "Heard Is. proxy"),
]

REGION_COLORS = {
    "Europe":      "#FF9800",
    "Americas":    "#E91E63",
    "Africa":      "#9C27B0",
    "Oceania":     "#00BCD4",
    "Asia":        "#F44336",
    "Australia":   "#4CAF50",
}

NETWORK_MARKERS = {
    "IU": "o",
    "AU": "s",
    "GE": "D",
    "MN": "P",
    "II": "h",
    "AV": "^",
    "CM": "v",
    "AF": "*",
    "FR": "X",
    "3D": "p",
}

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi  = np.radians(lat2 - lat1)
    dlam  = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlam/2)**2
    return 2 * R * np.arcsin(np.sqrt(a))

def display_lon(lon):
    """Wrap longitude into MAP_WEST..MAP_EAST display range."""
    if lon < MAP_WEST:
        return lon + 360
    if lon > MAP_EAST:
        return lon - 360
    return lon

# Sort stations by distance from Hobart
STATIONS = sorted(_STATIONS_RAW,
                  key=lambda s: haversine(TAS_LAT, TAS_LON, s[1], s[2]))

# ── Figure layout ───────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(38, 22), facecolor="#0d1117")
fig.suptitle(
    "pyTREMOR — Seismic Station Network  (v2 · Global)\n"
    "Victor Mazon Gardoqui · Kräken.LABS",
    color="white", fontsize=18, y=0.985, fontweight="bold"
)

# ── MAP (left panel) ────────────────────────────────────────────────────────────
ax_map = fig.add_axes([0.01, 0.06, 0.56, 0.88])
ax_map.set_facecolor("#161b22")
ax_map.set_xlim(MAP_WEST, MAP_EAST)
ax_map.set_ylim(-72, 72)
ax_map.set_title("Global Station Locations — All Active Autoconfig Entries",
                 color="white", fontsize=13, pad=8)
ax_map.tick_params(colors="#555")
for spine in ax_map.spines.values():
    spine.set_edgecolor("#30363d")

# Grid
for lon in range(-120, 216, 30):
    ax_map.axvline(lon, color="#1f2937", lw=0.5, zorder=0)
for lat in range(-70, 71, 20):
    ax_map.axhline(lat, color="#1f2937", lw=0.5, zorder=0)

def lon_label(l):
    if l == 0:   return "0°"
    if l > 0:    return f"{l}°E"
    return f"{abs(l)}°W"

ax_map.set_xticks(range(-120, 216, 30))
ax_map.set_yticks(range(-70, 71, 20))
ax_map.set_xticklabels([lon_label(l) for l in range(-120, 216, 30)],
                        color="#888", fontsize=9)
ax_map.set_yticklabels([f"{abs(l)}°{'S' if l<0 else 'N'}" for l in range(-70, 71, 20)],
                        color="#888", fontsize=9)

# Ghost continent fills + outlines
for poly_pts in _CONTINENTS:
    xs = [display_lon(p[0]) for p in poly_pts]
    ys = [p[1] for p in poly_pts]
    ax_map.fill(xs, ys, color="#2a3a2a", alpha=0.20, zorder=0)
    ax_map.plot(xs + [xs[0]], ys + [ys[0]], color="#4a6a4a", alpha=0.28, lw=0.7, zorder=1)

# Hobart star
ax_map.plot(TAS_LON, TAS_LAT, "*", color="#FFD700", markersize=16, zorder=10,
            markeredgecolor="#0d1117", markeredgewidth=0.8)
ax_map.annotate("Hobart, Tasmania\n42.88°S  147.33°E",
                (TAS_LON, TAS_LAT), textcoords="offset points",
                xytext=(8, -26), color="#FFD700", fontsize=9.5, fontweight="bold")

# Draw connecting lines + station markers
for label, lat, lon, region, network, notes in STATIONS:
    dlon  = display_lon(lon)
    color  = REGION_COLORS[region]
    marker = NETWORK_MARKERS.get(network, "o")

    # Great-circle line approximation (straight line in equirectangular is ok here)
    ax_map.plot([TAS_LON, dlon], [TAS_LAT, lat],
                color=color, alpha=0.20, lw=0.9, zorder=1)

    ax_map.plot(dlon, lat, marker, color=color, markersize=11,
                markeredgecolor="#0d1117", markeredgewidth=0.8, zorder=5)

    short = label.split("\n")[0]
    ax_map.annotate(short, (dlon, lat), textcoords="offset points",
                    xytext=(6, 5), color=color, fontsize=8.5,
                    fontweight="bold", zorder=6)

# ── TABLE (right panel) ─────────────────────────────────────────────────────────
ax_tbl = fig.add_axes([0.59, 0.06, 0.40, 0.88])
ax_tbl.set_facecolor("#161b22")
ax_tbl.axis("off")
ax_tbl.set_title("Station Reference", color="white", fontsize=15, pad=10)

col_headers = ["Station", "Net", "Region / Volcano", "Coordinates", "km"]
col_x       = [0.00, 0.17, 0.27, 0.60, 0.92]
row_h  = 0.044
header_y = 0.97

for i, h in enumerate(col_headers):
    ax_tbl.text(col_x[i], header_y, h, color="#FFD700", fontsize=12,
                fontweight="bold", transform=ax_tbl.transAxes, va="top")

ax_tbl.plot([0, 1], [header_y - 0.011, header_y - 0.011],
            color="#30363d", lw=0.8, transform=ax_tbl.transAxes, clip_on=False)

for idx, (label, lat, lon, region, network, notes) in enumerate(STATIONS):
    y      = header_y - 0.025 - idx * row_h
    color  = REGION_COLORS[region]
    dist   = int(haversine(TAS_LAT, TAS_LON, lat, lon))
    short  = label.replace("\n", " ")

    if idx % 2 == 0:
        rect = mpatches.FancyBboxPatch(
            (0, y - row_h * 0.75), 1, row_h * 0.92,
            boxstyle="square,pad=0", facecolor="#1c2128", edgecolor="none",
            transform=ax_tbl.transAxes, zorder=0)
        ax_tbl.add_patch(rect)

    ax_tbl.text(col_x[0], y, short, color=color, fontsize=11,
                transform=ax_tbl.transAxes, va="top", fontweight="bold")
    ax_tbl.text(col_x[1], y, network, color="#aaa", fontsize=11,
                transform=ax_tbl.transAxes, va="top")
    ax_tbl.text(col_x[2], y, notes, color="#ccc", fontsize=10.5,
                transform=ax_tbl.transAxes, va="top")
    lat_str = (f"{abs(lat):.2f}°{'S' if lat<0 else 'N'}  "
               f"{abs(lon):.2f}°{'W' if lon<0 else 'E'}")
    ax_tbl.text(col_x[3], y, lat_str, color="#7a9fc2", fontsize=10.5,
                transform=ax_tbl.transAxes, va="top")
    ax_tbl.text(col_x[4], y, f"{dist:,}", color="#888", fontsize=11,
                transform=ax_tbl.transAxes, va="top", ha="left")

# ── Legends ─────────────────────────────────────────────────────────────────────
seen_regions = {}
for _, _, _, region, _, _ in STATIONS:
    if region not in seen_regions:
        seen_regions[region] = REGION_COLORS[region]

region_patches = [
    mpatches.Patch(color=c, label=r)
    for r, c in seen_regions.items()
]
network_handles = [
    Line2D([0], [0], marker=m, color="w", markerfacecolor="#aaa",
           markersize=7, label=f"{n} network", linestyle="None")
    for n, m in NETWORK_MARKERS.items()
    if any(s[4] == n for s in STATIONS)
]
tas_handle = Line2D([0], [0], marker="*", color="w", markerfacecolor="#FFD700",
                    markersize=10, label="Hobart (base)", linestyle="None")

ax_map.legend(
    handles=region_patches + network_handles + [tas_handle],
    loc="lower left", fontsize=9.5, framealpha=0.35,
    facecolor="#0d1117", edgecolor="#30363d", labelcolor="white",
    ncol=2
)

out_path = "docs/pyTREMOR_stations_v2.png"
plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="#0d1117")
print(f"[+] Saved: {out_path}")
