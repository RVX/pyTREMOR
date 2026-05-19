# pyTREMOR — Seismic Station Reference
**Location base:** Tasmania, Australia  
**Data source:** FDSN / EarthScope (IRIS) seismic network  
**Last updated:** May 2026

---

## How it works

pyTREMOR fetches real seismic waveform data from global FDSN servers and **sonifies** it — converting ground motion recorded by seismometers into audio-visual output (spectrogram + sound). Each station streams continuous broadband seismic data that captures both local and teleseismic events including volcanic tremor, eruption signals, and tectonic earthquakes.

### Key parameters used across all stations
| Parameter | Value | Meaning |
|---|---|---|
| `freqmin` | 1 Hz | Low-end frequency filter |
| `freqmax` | 23 Hz | High-end frequency filter |
| `channel` | BHZ / HHZ | Vertical broadband (BHZ = 40 sps, HHZ = 100 sps) |
| `speed_up_factor` | 200 | Playback speed multiplier (seismic → audible) |
| `fps` | 1 | Frames per second in output video |
| `spec_win_dur` | 8 s | Spectrogram window duration |
| `db_lim` | -180 / -130 dB | Dynamic range for spectrogram colour scale |
| `LASTHOURS` | 5 | Hours of data fetched per run |

---

## OCEANIA — Active Volcanoes (closest to Tasmania)

> Australia sits in the stable interior of the Indo-Australian plate with no active mainland volcanoes. The nearest active volcanic systems are in New Zealand (~2,000 km) along the Pacific Ring of Fire.

### New Zealand — Taupo Volcanic Zone
*Network: NZ (GeoNet) — High-frequency broadband HHZ*

| Label | Station | Volcano / Location | Type | Distance from Tas. |
|---|---|---|---|---|
| `NZ_WHITEISLAND` | WHVZ | Whakaari / White Island | Active stratovolcano — near-continuous eruption | ~2,000 km |
| `NZ_RUAPEHU` | KRVZ | Ruapehu | Active stratovolcano — frequent lahars & eruptions | ~2,100 km |
| `NZ_TONGARIRO` | OTVZ | Tongariro / Ngauruhoe | Active volcanic complex — erupted 2012 | ~2,100 km |
| `NZ_TAUPO` | FWVZ | Taupo Volcanic Zone | Supervolcano / geothermal system — world's most productive | ~2,100 km |

**Note:** GeoNet stations (NZ network) require the GeoNet FDSN endpoint. If they return "not replying" via EarthScope, they need a custom server URL.

### New Zealand — GSN Reference Station
*Network: IU (Global Seismograph Network)*

| Label | Station | Location | Notes |
|---|---|---|---|
| `NZ_WELLINGTON` | SNZO | South Karori, Wellington | GSN broadband — reliable via EarthScope, near Cook Strait |

### Papua New Guinea
*Network: AU (Australian National Seismograph Network)*

| Label | Station | Volcano / Location | Type | Distance from Tas. |
|---|---|---|---|---|
| `PNG_RABAUL` | RABL | Rabaul / Tavurvur | Caldera complex — Tavurvur destroyed Rabaul town 1994 | ~3,800 km |

### Solomon Islands
*Network: IU (Global Seismograph Network)*

| Label | Station | Location | Notes |
|---|---|---|---|
| `SOLOMON_HNR` | HNR | Honiara | Near Tinakula (active stratovolcano, one of Pacific's most remote) |

### Samoa
*Network: IU (Global Seismograph Network)*

| Label | Station | Location | Notes |
|---|---|---|---|
| `SAMOA_AFI` | AFI | Afiamalu, Samoa | Near Samoa hotspot — 2009 submarine eruption in the region |

---

## ASIA — Active Volcanic Zones

> Asia hosts the densest concentration of active volcanoes on Earth, dominated by the Pacific Ring of Fire (Japan, Kamchatka, Philippines) and the Sunda Arc (Indonesia).

### Japan
*Network: IU (Global Seismograph Network)*

| Label | Station | Location | Nearby Volcanoes | Distance from Tas. |
|---|---|---|---|---|
| `JP_MAJO` | MAJO | Matsushiro, Nagano | Asama (active), Ontake (2014 eruption killed 63), Norikura | ~8,000 km |

**Ontake context:** The 2014 phreatic eruption of Ontake was the deadliest volcanic disaster in Japan since 1926. Seismic precursors were minimal — exactly the kind of signal pyTREMOR is designed to study.

### Kamchatka, Russia
*Network: IU (Global Seismograph Network)*

| Label | Station | Location | Nearby Volcanoes | Distance from Tas. |
|---|---|---|---|---|
| `KAMCHATKA_PET` | PET | Petropavlovsk-Kamchatsky | Klyuchevskoy (one of world's most active), Shiveluch, Bezymianny | ~9,000 km |

**Klyuchevskoy context:** Has been in near-continuous eruption since 1700. Eruptions reach 15–20 km ash columns regularly. One of the most prolific volcanic sources of SO₂ on Earth.

### Philippines
*Network: IU (Global Seismograph Network)*

| Label | Station | Location | Nearby Volcanoes | Distance from Tas. |
|---|---|---|---|---|
| `PH_DAV` | DAV | Davao, Mindanao | Apo (highest peak in PH), Parker, Hibok-Hibok, Ragang | ~6,500 km |

### Mariana Arc
*Network: IU (Global Seismograph Network)*

| Label | Station | Location | Notes | Distance from Tas. |
|---|---|---|---|---|
| `MARIANA_GUMO` | GUMO | Guam | Active submarine arc volcanoes — NW Rota-1, Ahyi Seamount | ~6,000 km |

### Indonesia — Sunda Arc
*Network: GE (GEOFON / GFZ Potsdam)*

| Label | Station | Location | Nearby Volcanoes | Distance from Tas. |
|---|---|---|---|---|
| `INDONESIA_GSI` | GSI | Gunung Sitoli, Nias | Sinabung (ongoing eruption since 2010), Toba supervolcano caldera | ~5,500 km |

**Toba context:** The Toba supervolcano eruption ~74,000 years ago is the largest known explosive eruption in the last 2 million years. The caldera is still geothermally active.

### Taiwan
*Network: IU (Global Seismograph Network)*

| Label | Station | Location | Nearby Volcanoes | Distance from Tas. |
|---|---|---|---|---|
| `TAIWAN_TATO` | TATO | Taipei | Tatun volcanic group — considered potentially active, last eruption ~6,000 years ago | ~7,500 km |

---

## AUSTRALIA — Volcanic Territories

> No active volcanoes exist on the Australian continent. The last eruptions occurred ~5,000–8,000 years ago (Mt Gambier, SA; Newer Volcanics Province, VIC). However, Australia administers two volcanically significant subantarctic territories.

| Label | Station | Network | Location | Notes |
|---|---|---|---|---|
| `AU_MACQUARIE` | MCQ | AU | Macquarie Island | ~1,500 km SE of Tasmania. Geologically active — sits on the Macquarie Ridge, one of Earth's most seismically active oceanic ridges. UNESCO World Heritage Site. |
| `AU_NWAO` | NWAO | IU (GSN) | Narrogin, Western Australia | Best mainland proxy for detecting events near **Heard Island** (Big Ben / Mawson Peak — one of the Southern Hemisphere's most active volcanoes, ~4,000 km SW of Perth). |

### Heard Island — Big Ben / Mawson Peak
Although no permanent seismic station exists on Heard Island, it is Australia's only confirmed **currently active** volcano:
- Eruptions detected regularly via satellite thermal imaging (MODIS/VIIRS)
- Lava flows have extended to the sea on multiple occasions since 2000
- Monitored remotely by Geoscience Australia via satellite and the AU network

---

## Network Reference

| Code | Name | Operator | Access |
|---|---|---|---|
| IU | Global Seismograph Network (GSN) | USGS / IRIS | EarthScope (IRISDMC) |
| AU | Australian National Seismograph Network | Geoscience Australia | EarthScope / AusPass |
| NZ | GeoNet New Zealand | GNS Science | GeoNet FDSN server |
| GE | GEOFON Network | GFZ Potsdam, Germany | GEOFON / EarthScope |
| AV | Alaska Volcano Observatory | USGS AVO | EarthScope |

---

## Running pyTREMOR

```bash
# Run all active stations in autoconfig (last N hours)
python pyTREMOR.py --autorun

# Interactive shell
python pyTREMOR.py

# Command line (single station)
python pyTREMOR.py --cmd IU SNZO BHZ 2026,5,19,0,0 2026,5,19,5,0 23 1 200 1 8 -180,-130
```

Output files are saved to `dataset/` as `.mp4` (spectrogram video + audio).

---

*pyTREMOR v0.5 — by Victor Mazon Gardoqui, supported by Kräken.LABS — root /at/ victormazon.com*
