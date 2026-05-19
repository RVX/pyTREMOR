
![c](https://03c8.net/images/pytremor-banner.png)

----------

#### Info:
 
 Seismoacoustics — the combined study of vibrations in the Earth and sound waves in the atmosphere 
to characterize non-earthquake geohazards, such as avalanches, landslides, and volcanic eruptions.

pyTREMOR fetches real seismic waveform data from global FDSN/EarthScope servers and sonifies it —
converting ground motion into spectrogram video + audio (MP4). Configured for near-real-time 
monitoring of active volcanic regions across Oceania, Asia, and Australia from a base in Hobart, Tasmania.

----------

#### Station Network (12 active stations):

| Region | Stations |
|---|---|
| New Zealand | SNZO (Wellington / GSN) |
| Oceania | RABL (Rabaul/PNG), HNR (Solomon Is.), AFI (Samoa) |
| Asia | MAJO (Japan), PET (Kamchatka), DAV (Philippines), GUMO (Mariana), GSI (Indonesia), TATO (Taiwan) |
| Australia | MCQ (Macquarie Is.), NWAO (Narrogin / Heard Is. proxy) |

All stations use IU (GSN), AU, or GE networks via EarthScope. Time windows are always calculated 
in UTC (`utcnow()`) for near-real-time accuracy. Default: last 5 hours.

----------

#### Installing:

 This tool runs on many platforms and it requires Python (3.x.y). You can install all related libs running this command:
 
 python3 setup.py install

#### Launching:
  
 python3 pytremor.py --help

#### Autorun (all configured stations, last N hours):

 python3 pyTREMOR.py --autorun

----------

#### License:

 PyTremor is released under the GPLv3.

#### Contact:

      - root /at/ victormazon.com

#### Contribute: 

 To make donations use the following hashes:
  
     - Bitcoin: 19aXfJtoYJUoXEZtjNwsah2JKN9CK5Pcjw
     - Ecoin: ETsRCBzaMawx3isvb5svX7tAukLdUFHKze

