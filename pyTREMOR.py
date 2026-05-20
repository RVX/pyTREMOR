#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pyTREMOR - Python /Seismoacoustics/ Squeezer - 2023-2024 - by Victor Mazon Gardoqui, supported by Kräken.LABS

----------

Seismoacoustics — the combined study of vibrations in the Earth and sound waves in the atmosphere 
to characterize non-earthquake geohazards, such as avalanches, landslides, and volcanic eruptions.

root /at/ victormazon.com

----------

You should have received a copy of the GNU General Public License along
with PyTREMOR; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""
VERSION = str(0.5)

import datetime
from datetime import timedelta
import os, sys
import shutil
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame
import subprocess
from obspy import UTCDateTime

import warnings
warnings.filterwarnings('ignore', message='Font family.*cursive')

def banner():
    print(r'''    __   _______         __  __            
 _ _\ \ / /_   _| __ ___|  \/  | ___  _ __ 
| '_ \ V /  | || '__/ _ \ |\/| |/ _ \| '__|
| |_) | |   | || | |  __/ |  | | (_) | |   
| .__/|_|   |_||_|  \___|_|  |_|\___/|_|   
|_|  pyTREMOR (v'''+VERSION+''') by Victor Mazon Gardoqui | supported by Kräken.LABS
    ''')

import os
import shutil
import datetime
from obspy import UTCDateTime

def sonify(network_conf, station_conf, channel_conf, starttime_conf, endtime_conf, freqmax_conf, freqmin_conf, speed_up_factor_conf, fps_conf, spec_win_dur_conf, db_lim_conf, location_conf='*'):
    db_lim_conf = db_lim_conf.replace("\n", "")
    db_lim_conf_1 = int(db_lim_conf.split(",")[0])
    db_lim_conf_2 = int(db_lim_conf.split(",")[1])

    from sonify.sonify.sonify import sonify

    try:
        print(f"\nSonifying data for: {station_conf}...")
        result = sonify(
            network=network_conf.replace("\n", ""),
            station=station_conf.replace("\n", ""),
            channel=channel_conf.replace("\n", ""),
            location=str(location_conf).replace("\n", ""),
            starttime=UTCDateTime(starttime_conf),
            endtime=UTCDateTime(endtime_conf),
            freqmax=int(freqmax_conf.replace("\n", "")),
            freqmin=int(freqmin_conf.replace("\n", "")),
            speed_up_factor=int(speed_up_factor_conf.replace("\n", "")),
            fps=int(fps_conf.replace("\n", "")),
            spec_win_dur=int(spec_win_dur_conf.replace("\n", "")),
            db_lim=(db_lim_conf_1, db_lim_conf_2),
        )
        print("Sonification completed successfully.")
        now = datetime.datetime.now()
        filename = now.strftime("%Y-%m-%d-%H-%M-") + station_conf.replace("\n", "") + ".mp4"
        dataset_folder = "dataset"
        if not os.path.exists(dataset_folder):
            os.makedirs(dataset_folder)
        new_filepath = os.path.join(dataset_folder, filename)  
        mp4_files = [file for file in os.listdir(".") if file.endswith(".mp4")]
        if mp4_files:
            mp4_file = mp4_files[0] 
            shutil.move(mp4_file, new_filepath)
            print(f"Video moved and renamed to: {new_filepath}")
            if "--autorun" not in sys.argv:
                menu()
        else:
            print("No .mp4 file found in the directory.")
        return True
    except Exception as e:
        print(f"An error occurred during sonification: This station is not replying!")
        return False

def menu():
    main_menu = {
        "(h)elp    ":"show this message",
        "(v)ersion ":"current version",
        "(c)lear   ":"clear screen",
        "(q)uit    ":"quit program"
    }
    sonification_menu = {
        "(setup)   ":"setup template",
        "(view)    ":"view template",
        "(run)     ":"run template",
        "(play)    ":"play sonification"
    }
    clear()
    while 1:
        cmd = input("pyTREMOR@GSN% ")
        if cmd == "h" or cmd == "help":
            print()
            for n in main_menu:
                print("    "+ n + ": " + main_menu[n])
            print()
            for n in sonification_menu:
                print("    "+ n + ": " + sonification_menu[n])
            print()
        elif cmd == "v" or cmd == "version":
            banner()
        elif cmd == "c" or cmd == "clear":
            clear()
        elif cmd == "setup":
            setup()
        elif cmd == "view":
            view()
        elif cmd == "run":
            run_from_config_file()
        elif cmd == "play":
            play_sonification()
        elif cmd == "q" or cmd == "quit" or cmd == "exit":
            quit()

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def quit():
    sys.exit()
    
def read_config(file):
    if file == "config":
        f = open("config","r")
    else:
        f = open("autoconfig","r")   
    lines = f.readlines()
    f.close()
    return lines
    
import subprocess

def play_sonification():
    dataset_folder = "dataset"
    if not os.path.exists(dataset_folder):
        print("No sonification files found.")
        return
    
    mp4_files = [file for file in os.listdir(dataset_folder) if file.endswith(".mp4")]
    wav_files = [file for file in os.listdir(dataset_folder) if file.endswith(".wav")]

    files = []
    for mp4_file in mp4_files:
        base_name = os.path.splitext(mp4_file)[0]
        if f"{base_name}.wav" in wav_files:
            files.append(mp4_file)
        else:
            files.append(mp4_file)

    if not files:
        print("No sonification files found.")
        return

    print("Available sonification files:")
    for i, filename in enumerate(files):
        print(f"{i+1}. {filename}")
    
    selection = input("Choose a file to play (enter number): ")
    try:
        selection = int(selection)
        if selection < 1 or selection > len(files):
            print("Invalid selection.")
            return
        selected_file = files[selection - 1]
        mp4_file = os.path.join(dataset_folder, selected_file)
        wav_file = os.path.splitext(selected_file)[0] + ".wav"
        wav_path = os.path.join(dataset_folder, wav_file)
        if not os.path.exists(wav_path):
            subprocess.run(["ffmpeg", "-i", mp4_file, wav_path])
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load(wav_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.quit()
    except ValueError:
        print("Invalid input. Please enter a number.")

def setup():
    network = input("\n    set network (str) (ex: AV): ")
    station = input("    set station (str) (ex: ILSW): ")
    channel = input("    set channel (str) (ex: BHZ): ")
    starttime = input("    set starttime (ex: 2019, 6, 20, 23, 10): ")
    endtime = input("    set endtime (ex: 2019, 6, 21, 0, 30): ")
    freqmin = input("    set freqmin (int or float) (ex: 1): ")
    freqmax = input("    set freqmax (int or float) (ex: 23): ")
    speed_up_factor = input("    set speed_up_factor (int) (ex: 200): ")
    fps = input("    fps (int) (ex: 1): ")
    spec_win_dur = input("    set spec_win_dur (int or float) (ex: 8): ")
    db_lim = input("    set db_lim (tuple or str) (ex: -180,-130): ")
    
    with open("config", mode='w') as config:
        config.write("network="+network+"\n")
        config.write("station="+station+"\n")
        config.write("channel="+channel+"\n")
        config.write("starttime="+starttime+"\n")
        config.write("endtime="+endtime+"\n")
        config.write("freqmin="+freqmin+"\n")
        config.write("freqmax="+freqmax+"\n")
        config.write("speed_up_factor="+speed_up_factor+"\n")
        config.write("fps="+fps+"\n")          
        config.write("spec_win_dur="+spec_win_dur+"\n")       
        config.write("db_lim="+db_lim)       
        config.close()

def view():
    if os.path.isfile("config"):
       lines = read_config("config") 
    else:
       with open("config", mode='w') as config:
           config.write("network=\n")
           config.write("station=\n")
           config.write("channel=\n")
           config.write("starttime=\n")
           config.write("endtime=\n")
           config.write("freqmin=\n")
           config.write("freqmax=\n")
           config.write("speed_up_factor=\n")
           config.write("fps=\n")          
           config.write("spec_win_dur=\n")       
           config.write("db_lim=")       
           config.close()      
       lines = read_config("config")      
    print("\n", "sonify(")
    for line in lines:
        line = line.replace("\n","")
        print("       ",line)
    print("       )\n")

def run(network_conf, station_conf, channel_conf, starttime_conf, endtime_conf, freqmax_conf, freqmin_conf, speed_up_factor_conf, fps_conf, spec_win_dur_conf, db_lim_conf):
    print("\n[+] Generating -sonify- setup from LOCAL config...")
    if os.path.isfile("config"):
       lines = read_config("config") 
    else:
       print("\n[Error] not 'config' file generated... Exiting!\n")
       sys.exit(2)

    for line in lines:   
        if "network" in line:
            network_conf = line.split("=")[1]
        if "station" in line:
            station_conf = line.split("=")[1]
        if "channel" in line:
            channel_conf = line.split("=")[1]
        if "starttime" in line:
            starttime_conf = line.split("=")[1]    
        if "endtime" in line:
            endtime_conf = line.split("=")[1]        
        if "freqmax" in line:
            freqmax_conf = line.split("=")[1]
        if "freqmin" in line:
            freqmin_conf = line.split("=")[1]
        if "speed_up_factor" in line:
            speed_up_factor_conf = line.split("=")[1]            
        if "fps" in line:
            fps_conf = line.split("=")[1]
        if "spec_win_dur" in line:
            spec_win_dur_conf = line.split("=")[1]
        if "db_lim" in line:
            db_lim_conf = line.split("=")[1] 

        success = sonify(network_conf, station_conf, channel_conf, starttime_conf, endtime_conf, freqmax_conf, freqmin_conf, speed_up_factor_conf, fps_conf, spec_win_dur_conf, db_lim_conf)

def run_from_config_file():
    lines = read_config("config")
    network_conf = ""
    station_conf = ""
    channel_conf = ""
    starttime_conf = ""
    endtime_conf = ""
    freqmax_conf = ""
    freqmin_conf = ""
    speed_up_factor_conf = ""
    fps_conf = ""
    spec_win_dur_conf = ""
    db_lim_conf = ""
    for line in lines:
        if "network" in line:
            network_conf = line.split("=")[1]
        if "station" in line:
            station_conf = line.split("=")[1]
        if "channel" in line:
            channel_conf = line.split("=")[1]
        if "starttime" in line:
            starttime_conf = line.split("=")[1]
        if "endtime" in line:
            endtime_conf = line.split("=")[1]
        if "freqmax" in line:
            freqmax_conf = line.split("=")[1]
        if "freqmin" in line:
            freqmin_conf = line.split("=")[1]
        if "speed_up_factor" in line:
            speed_up_factor_conf = line.split("=")[1]
        if "fps" in line:
            fps_conf = line.split("=")[1]
        if "spec_win_dur" in line:
            spec_win_dur_conf = line.split("=")[1]
        if "db_lim" in line:
            db_lim_conf = line.split("=")[1]

    success = run(network_conf, station_conf, channel_conf, starttime_conf, endtime_conf, freqmax_conf, freqmin_conf, speed_up_factor_conf, fps_conf, spec_win_dur_conf, db_lim_conf)
    if success:
        menu()

def init():
    if "--cmd" in sys.argv:
        try:
            network_conf = sys.argv[2]+"\n"
            station_conf = sys.argv[3]+"\n"
            channel_conf = sys.argv[4]+"\n"
            starttime_conf = sys.argv[5].replace(",",", ")+"\n"
            endtime_conf = sys.argv[6].replace(",",", ")+"\n"
            freqmax_conf = sys.argv[7]+"\n"
            freqmin_conf = sys.argv[8]+"\n"
            speed_up_factor_conf = sys.argv[9]+"\n"
            fps_conf = sys.argv[10]+"\n"
            spec_win_dur_conf = sys.argv[11]+"\n"
            db_lim_conf = sys.argv[12]+"\n"
            print("\n[+] Generating -sonify- setup from CMD config...")
            print("\n", "sonify(")  
            print("       network="+network_conf.replace("\n",""))
            print("       station="+station_conf.replace("\n",""))
            print("       channel="+channel_conf.replace("\n",""))
            print("       starttime="+starttime_conf.replace("\n",""))
            print("       endtime="+endtime_conf.replace("\n",""))
            print("       freqmax="+freqmax_conf.replace("\n",""))
            print("       freqmin="+freqmin_conf.replace("\n",""))
            print("       speed_up_factor="+speed_up_factor_conf.replace("\n",""))
            print("       fps="+fps_conf.replace("\n",""))
            print("       spec_win_dur="+spec_win_dur_conf.replace("\n",""))
            print("       db_lim="+db_lim_conf)
            print("       )")     
            success = sonify(network_conf, station_conf, channel_conf, starttime_conf, endtime_conf, freqmax_conf, freqmin_conf, speed_up_factor_conf, fps_conf, spec_win_dur_conf, db_lim_conf)
            if success:
                menu()
        except:
            print("\n[Error] Executing parameters are wrong... Please review your command line!") 
            print("\n    +SYNTAX:\n       python3 pyTREMOR.py --cmd <network> <station> <channel> <starttime> <endtime> <freqmax> <freqmin> <speed_up_factor> <fps> <spec_win_dur> <db_lim>")
            print("\n    +EXAMPLE:\n       python3 pyTREMOR.py --cmd AV ILSW BHZ 2019,6,20,23,10 2019,6,21,0,30 23 1 200 1 8 -180,-130\n")
            
    elif "--autorun" in sys.argv:
        print("\n[+] Generating -sonify- setup from LOCAL auto-config...")
        if os.path.isfile("autoconfig"):
            lines = read_config("autoconfig") 
        else:
            print("\n[Error] not 'autoconfig' file found... Exiting!\n")
            sys.exit(2)      
        datetime_format = "%Y, %m, %d, %H, %M"           
        endtime_conf = datetime.datetime.utcnow()
        endtime_conf_format = endtime_conf.strftime(datetime_format)
        print("\n"+"-"*24)
        for line in lines:
            if "LASTHOURS" in line:
                lasthours = line.split("=")[1]    
                print ("[Info] LAST HOURS: ["+ str(lasthours).replace("\n","")+"]")
        starttime_conf = endtime_conf - timedelta(hours=int(lasthours))
        starttime_conf_format = starttime_conf.strftime(datetime_format)       
        print ("[Info] Starttime: "+str(starttime_conf_format))
        print ("[Info] Endtime: "+ str(endtime_conf_format))
        print("-"*24+"\n")
        stations_list=[]
        for line in lines:
            if "#" in line:
                location = line.split("{")[0]
                print (location)
                location_conf = line.split("{")[1]
                location_conf = location_conf.replace("{", "")
                location_conf = location_conf.replace("}", "")   
                location_conf = location_conf.replace("\n", "")   
                location_list = list(location_conf.split(","))
                location_list.append("starttime="+starttime_conf_format)
                location_list.append("endtime="+endtime_conf_format)
                location_list.append("label="+location.replace("#","").strip())
                print("  "+ str(location_list)+"\n")
                stations_list.append(location_list)
        print("-"*24+"\n")
        autorun_results = []
        for station in stations_list:
            location_conf = '*'
            label_conf = ''
            for value in station:
                if "network" in value:
                    network_conf = value.split("=")[1]
                if "station" in value:
                    station_conf = value.split("=")[1]
                if "channel" in value:
                    channel_conf = value.split("=")[1]
                if "starttime" in value:
                    starttime_conf = value.split("=")[1]    
                if "endtime" in value:
                    endtime_conf = value.split("=")[1]        
                if "freqmax" in value:
                    freqmax_conf = value.split("=")[1]
                if "freqmin" in value:
                    freqmin_conf = value.split("=")[1]
                if "speed_up_factor" in value:
                    speed_up_factor_conf = value.split("=")[1]            
                if "fps" in value:
                    fps_conf = value.split("=")[1]
                if "spec_win_dur" in value:
                    spec_win_dur_conf = value.split("=")[1]
                if "db_lim" in value:
                    db_lim_conf_1 = value.split("|")[0]
                    db_lim_conf_1 = db_lim_conf_1.split("=")[1]
                    db_lim_conf_2 = value.split("|")[1]
                    db_lim_conf=(db_lim_conf_1+","+db_lim_conf_2)
                if "location" in value:
                    location_conf = value.split("=")[1]
                if "label" in value:
                    label_conf = value.split("=")[1]
            success = sonify(network_conf, station_conf, channel_conf, starttime_conf, endtime_conf, freqmax_conf, freqmin_conf, speed_up_factor_conf, fps_conf, spec_win_dur_conf, db_lim_conf, location_conf)
            autorun_results.append((label_conf or station_conf.strip(), station_conf.strip(), success))

        n_ok   = sum(1 for _, _, s in autorun_results if s)
        n_fail = sum(1 for _, _, s in autorun_results if not s)
        width  = 44
        print("\n" + "="*width)
        print("  AUTORUN SUMMARY".center(width))
        print("="*width)
        for label, station, ok in autorun_results:
            status = "[OK]  " if ok else "[FAIL]"
            print(f"  {status}  {label:<22}  {station}")
        print("-"*width)
        print(f"  {n_ok}/{len(autorun_results)} stations completed".ljust(width-1))
        print("="*width + "\n")

    if "--help" in sys.argv:
        print("="*50)
        banner()
        print(" Seismoacoustics — the combined study of vibrations in the Earth and sound waves in the atmosphere\n to characterize non-earthquake geohazards, such as avalanches, landslides, and volcanic eruptions.\n")
        print("="*50)
        print("    +HELP:\n       python3 pyTREMOR.py --help")
        print("-"*50)
        print("\n    +SHELL:\n       python3 pyTREMOR.py")
        print("\n    +AUTORUN:\n       python3 pyTREMOR.py --autorun")
        print("\n    +CMD:\n       python3 pyTREMOR.py --cmd <network> <station> <channel> <starttime> <endtime> <freqmax> <freqmin> <speed_up_factor> <fps> <spec_win_dur> <db_lim>\n")
    else:
        menu()

init()

