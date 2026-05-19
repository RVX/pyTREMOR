
<div align="center">

![pyTREMOR](https://03c8.net/images/pytremor-banner.png)

**Seismoacoustics tool for real-time volcanic monitoring**

*by Victor Mazon Gardoqui — [victormazon.com](https://victormazon.com)*

</div>

---

## What is pyTREMOR?

**Seismoacoustics** is the combined study of vibrations in the Earth and sound waves in the atmosphere, used to characterize non-earthquake geohazards such as avalanches, landslides, and volcanic eruptions.

pyTREMOR fetches live seismic waveform data from global FDSN/EarthScope servers and **sonifies** it — converting ground motion into spectrogram video + audio (MP4). Configured for near-real-time monitoring of active volcanic regions across Oceania, Asia, and Australia, referenced from Hobart, Tasmania.

---

## Station Network — 12 active stations

| Region | Stations |
|--------|----------|
| 🇳🇿 New Zealand | SNZO (Wellington / GSN) |
| 🌊 Oceania | RABL (Rabaul/PNG), HNR (Solomon Is.), AFI (Samoa) |
| 🌏 Asia | MAJO (Japan), PET (Kamchatka), DAV (Philippines), GUMO (Mariana), GSI (Indonesia), TATO (Taiwan) |
| 🦘 Australia | MCQ (Macquarie Is.), NWAO (Narrogin / Heard Is. proxy) |

All stations use **IU (GSN)**, **AU**, or **GE** networks via EarthScope. Time windows are calculated in UTC for near-real-time accuracy. Default window: last **5 hours**.

![Station Map](docs/pyTREMOR_stations.png)

---

## Install

Requires Python 3.x. Install dependencies with:

```bash
python3 setup.py install
```

---

## Usage

```bash
# Help
python3 pyTREMOR.py --help

# Interactive mode
python3 pyTREMOR.py --cmd

# Autorun — all configured stations, last N hours
python3 pyTREMOR.py --autorun
```

---

## License

pyTREMOR is released under the **GPLv3**.

---

## Contact

✉️ root /at/ victormazon.com

---

## Donate

If you find pyTREMOR useful, consider supporting development:

| Currency | Address |
|----------|---------|
| ₿ Bitcoin | `19aXfJtoYJUoXEZtjNwsah2JKN9CK5Pcjw` |
| Ξ Ecoin | `ETsRCBzaMawx3isvb5svX7tAukLdUFHKze` |

