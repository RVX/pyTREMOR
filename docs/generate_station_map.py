#!/usr/bin/env python3
"""
pyTREMOR — Station Map Generator
Generates a visual chart of all configured seismic stations.
by Victor Mazon Gardoqui, supported by Kräken.LABS — root /at/ victormazon.com
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.collections import PatchCollection
import numpy as np

# ── Simplified continent outlines (lon, lat) in map coords 60–220E ─────────────
# Approximate polygons for a ghost/transparent continent background
_CONTINENTS = [
    # Australia
    [(114,-22),(122,-18),(130,-12),(137,-13),(140,-17),(146,-19),(151,-24),(154,-28),
     (153,-32),(151,-34),(150,-38),(147,-39),(144,-38),(141,-36),(134,-33),(131,-32),
     (128,-34),(124,-34),(120,-34),(116,-32),(114,-28),(113,-25),(114,-22)],
    # New Zealand South
    [(166,-46),(168,-46),(170,-44),(172,-42),(172,-41),(170,-40),(168,-44),(166,-46)],
    # New Zealand North
    [(174,-41),(176,-40),(178,-38),(178,-37),(177,-38),(175,-40),(174,-41)],
    # Papua New Guinea + Indonesia east
    [(131,-3),(135,-6),(140,-8),(145,-8),(148,-6),(150,-6),(152,-5),(150,-9),(145,-10),
     (141,-9),(138,-8),(134,-6),(131,-3)],
    # Indonesia (Sumatra + Java rough)
    [(96,5),(100,4),(104,1),(106,-2),(108,-7),(110,-8),(114,-8),(116,-8),(118,-9),
     (120,-10),(118,-9),(115,-8),(110,-7),(106,-6),(104,-4),(102,-2),(100,2),(98,3),(96,5)],
    # Philippines
    [(118,8),(120,10),(122,12),(124,12),(126,10),(124,8),(122,7),(120,8),(118,8)],
    # Japan (Honshu approx)
    [(130,31),(132,33),(135,34),(137,35),(138,36),(140,37),(141,38),(141,40),
     (140,42),(138,40),(136,37),(134,35),(132,33),(130,31)],
    # Taiwan
    [(120,22),(121,22),(122,23),(122,25),(121,25),(120,24),(120,22)],
    # Kamchatka
    [(158,52),(160,54),(162,55),(163,57),(162,58),(160,57),(158,55),(156,53),(158,52)],
    # Guam area (tiny)
    [(144,13),(145,13),(145,14),(144,14),(144,13)],
    # Samoa (tiny)
    [(188,-14),(189,-14),(189,-13),(188,-13),(188,-14)],  # lon+360 = 188
    # Solomon Islands
    [(160,-9),(162,-9),(162,-8),(160,-8),(160,-9)],
    # Macquarie Island (tiny)
    [(158,-54),(159,-54),(159,-55),(158,-55),(158,-54)],
    # Mainland Asia (very rough eastern coast for context)
    [(100,0),(105,5),(108,15),(110,20),(115,25),(120,30),(122,32),(124,35),(126,38),
     (128,42),(130,45),(132,48),(135,50),(138,48),(135,45),(130,42),(128,38),(125,35),
     (122,30),(120,25),(115,20),(112,15),(108,10),(105,5),(100,0)],
]

# Hobart, Tasmania — base location
TAS_LAT, TAS_LON = -42.8821, 147.3272

# All stations: (label, lat, lon, region, network, volcano/notes)
# Sorted by distance from Hobart after haversine is defined — see below
_STATIONS_RAW = [
    # OCEANIA
    ("WHVZ\nWhite Is.", -37.52, 177.18, "Oceania NZ", "NZ", "Whakaari / active"),
    ("KRVZ\nRuapehu",   -39.28, 175.56, "Oceania NZ", "NZ", "Ruapehu / active"),
    ("OTVZ\nTongariro", -39.28, 175.54, "Oceania NZ", "NZ", "Tongariro / active"),
    ("FWVZ\nTaupo",     -38.69, 176.08, "Oceania NZ", "NZ", "Taupo supervolcano"),
    ("SNZO\nWellington",-41.31, 174.70, "Oceania NZ", "IU", "GSN broadband"),
    ("RABL\nRabaul",    -4.19,  152.16, "Oceania PNG","AU", "Tavurvur caldera"),
    ("HNR\nHoniara",    -9.44,  159.95, "Oceania",    "IU", "Near Tinakula"),
    ("AFI\nSamoa",     -13.91, -171.78, "Oceania",    "IU", "Samoa hotspot"),
    # ASIA
    ("MAJO\nJapan",     36.55,  138.20, "Asia",       "IU", "Asama / Ontake"),
    ("PET\nKamchatka",  53.02,  158.65, "Asia",       "IU", "Klyuchevskoy"),
    ("DAV\nPhilippines", 7.07,  125.58, "Asia",       "IU", "Apo / Mindanao"),
    ("GUMO\nGuam",      13.59,  144.87, "Asia",       "IU", "Mariana Arc"),
    ("GSI\nIndonesia",   1.30,   97.57, "Asia",       "GE", "Sinabung / Toba"),
    ("TATO\nTaiwan",    24.97,  121.50, "Asia",       "IU", "Tatun volcanic"),
    # AUSTRALIA
    ("MCQ\nMacquarie", -54.50,  158.94, "Australia",  "AU", "Macquarie Ridge"),
    ("NWAO\nNarrogin", -32.93,  117.24, "Australia",  "IU", "Heard Is. proxy"),
]

REGION_COLORS = {
    "Oceania NZ": "#2196F3",
    "Oceania PNG": "#03A9F4",
    "Oceania":     "#00BCD4",
    "Asia":        "#F44336",
    "Australia":   "#4CAF50",
}

NETWORK_MARKERS = {
    "IU": "o",
    "AU": "s",
    "NZ": "^",
    "GE": "D",
}

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlambda/2)**2
    return 2 * R * np.arcsin(np.sqrt(a))

# Sort stations by distance from Hobart
STATIONS = sorted(_STATIONS_RAW, key=lambda s: haversine(TAS_LAT, TAS_LON, s[1], s[2]))

# ── Figure layout ──────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(32, 20), facecolor="#0d1117")
fig.suptitle(
    "pyTREMOR — Seismic Station Network\nVictor Mazon Gardoqui",
    color="white", fontsize=18, y=0.98, fontweight="bold"
)

# ── MAP (left panel) ───────────────────────────────────────────────────────────
ax_map = fig.add_axes([0.01, 0.08, 0.52, 0.85])
ax_map.set_facecolor("#161b22")
ax_map.set_xlim(60, 220)
ax_map.set_ylim(-70, 65)
ax_map.set_title("Station Locations — Pacific / Asia / Southern Ocean",
                 color="white", fontsize=13, pad=8)
ax_map.tick_params(colors="#555")
for spine in ax_map.spines.values():
    spine.set_edgecolor("#30363d")

# Grid
for lon in range(60, 221, 30):
    ax_map.axvline(lon, color="#1f2937", lw=0.5, zorder=0)
for lat in range(-70, 66, 20):
    ax_map.axhline(lat, color="#1f2937", lw=0.5, zorder=0)
ax_map.set_xticks(range(60, 221, 30))
ax_map.set_yticks(range(-70, 66, 20))
ax_map.set_xticklabels([f"{l}°E" if l <= 180 else f"{360-l}°W" for l in range(60, 221, 30)],
                        color="#888", fontsize=10)
ax_map.set_yticklabels([f"{abs(l)}°{'S' if l<0 else 'N'}" for l in range(-70, 66, 20)],
                        color="#888", fontsize=10)

# Ghost continent outlines
for poly_pts in _CONTINENTS:
    xs = [p[0] if p[0] >= 60 else p[0]+360 for p in poly_pts]
    ys = [p[1] for p in poly_pts]
    ax_map.fill(xs, ys, color="#2a3a2a", alpha=0.18, zorder=0)
    ax_map.plot(xs + [xs[0]], ys + [ys[0]], color="#4a6a4a", alpha=0.25, lw=0.7, zorder=1)

# Tasmania star
ax_map.plot(TAS_LON, TAS_LAT, "*", color="#FFD700", markersize=16, zorder=10,
            markeredgecolor="#0d1117", markeredgewidth=0.8)
ax_map.annotate("Hobart, Tasmania\n42.88°S  147.33°E", (TAS_LON, TAS_LAT), textcoords="offset points",
                xytext=(8, -26), color="#FFD700", fontsize=10, fontweight="bold")

# Draw lines + stations
for label, lat, lon, region, network, notes in STATIONS:
    # wrap longitude for display
    dlon = lon if lon >= 60 else lon + 360
    color = REGION_COLORS[region]
    marker = NETWORK_MARKERS.get(network, "o")

    # line from Tasmania
    ax_map.plot([TAS_LON, dlon], [TAS_LAT, lat],
                color=color, alpha=0.25, lw=0.8, zorder=1)

    ax_map.plot(dlon, lat, marker, color=color, markersize=11,
                markeredgecolor="#0d1117", markeredgewidth=0.8, zorder=5)

    short = label.split("\n")[0]
    ax_map.annotate(short, (dlon, lat), textcoords="offset points",
                    xytext=(6, 5), color=color, fontsize=9, fontweight="bold", zorder=6)

# ── TABLE (right panel) ────────────────────────────────────────────────────────
ax_tbl = fig.add_axes([0.55, 0.08, 0.44, 0.85])
ax_tbl.set_facecolor("#161b22")
ax_tbl.axis("off")
ax_tbl.set_title("Station Reference", color="white", fontsize=16, pad=10)

col_headers = ["Station", "Net", "Region / Volcano", "Coordinates", "km"]
col_x       = [0.00, 0.17, 0.26, 0.58, 0.90]
row_h = 0.057
header_y = 0.97

# Header row
for i, h in enumerate(col_headers):
    ax_tbl.text(col_x[i], header_y, h, color="#FFD700", fontsize=13,
                fontweight="bold", transform=ax_tbl.transAxes, va="top")

ax_tbl.plot([0, 1], [header_y - 0.012, header_y - 0.012], color="#30363d", lw=0.8,
            transform=ax_tbl.transAxes, clip_on=False)

for idx, (label, lat, lon, region, network, notes) in enumerate(STATIONS):
    y = header_y - 0.03 - idx * row_h
    color = REGION_COLORS[region]
    dist = int(haversine(TAS_LAT, TAS_LON, lat, lon))
    short_label = label.replace("\n", " ")

    # alternating row bg
    if idx % 2 == 0:
        rect = mpatches.FancyBboxPatch((0, y - row_h*0.75), 1, row_h*0.9,
                                        boxstyle="square,pad=0",
                                        facecolor="#1c2128", edgecolor="none",
                                        transform=ax_tbl.transAxes, zorder=0)
        ax_tbl.add_patch(rect)

    ax_tbl.text(col_x[0], y, short_label, color=color, fontsize=12.5,
                transform=ax_tbl.transAxes, va="top", fontweight="bold")
    ax_tbl.text(col_x[1], y, network, color="#aaa", fontsize=12.5,
                transform=ax_tbl.transAxes, va="top")
    lat_str = f"{abs(lat):.2f}\u00b0{'S' if lat<0 else 'N'}  {abs(lon):.2f}\u00b0{'W' if lon<0 else 'E'}"
    ax_tbl.text(col_x[2], y, notes, color="#ccc", fontsize=12,
                transform=ax_tbl.transAxes, va="top")
    ax_tbl.text(col_x[3], y, lat_str, color="#7a9fc2", fontsize=12,
                transform=ax_tbl.transAxes, va="top")
    ax_tbl.text(col_x[4], y, f"{dist:,}", color="#888", fontsize=12.5,
                transform=ax_tbl.transAxes, va="top", ha="left")

# ── Legends ────────────────────────────────────────────────────────────────────
seen = {}
for _,_,_,region,_,_ in STATIONS:
    if region not in seen:
        seen[region] = REGION_COLORS[region]
region_patches = [mpatches.Patch(color=c, label=r.replace(" NZ","").replace(" PNG",""))
                  for r, c in seen.items()]
network_handles = [Line2D([0],[0], marker=m, color="w", markerfacecolor="#aaa",
                          markersize=7, label=f"{n} network", linestyle="None")
                   for n, m in NETWORK_MARKERS.items()]
tas_handle = Line2D([0],[0], marker="*", color="w", markerfacecolor="#FFD700",
                    markersize=10, label="Tasmania (base)", linestyle="None")

ax_map.legend(handles=region_patches + network_handles + [tas_handle],
              loc="lower left", fontsize=10, framealpha=0.3,
              facecolor="#0d1117", edgecolor="#30363d", labelcolor="white",
              ncol=2)

out_path = "docs/pyTREMOR_stations.png"
plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="#0d1117")
print(f"[+] Saved: {out_path}")
