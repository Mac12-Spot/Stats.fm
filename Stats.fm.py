import json
import inquirer
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import datetime, timedelta
import random

client_id = 'ENTER YOUR SPOTIFY CLIENT ID'
client_secret = 'ENTER YOUR SPOTIFY CLIENT SECRET'
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

def search_spotify_track(track_name, artist_name, album_name):
    query = f"track:{track_name} artist:{artist_name} album:{album_name}"
    result = sp.search(q=query, type='track', limit=1)
    if result['tracks']['items']:
        track = result['tracks']['items'][0]
        return {
            "spotify_track_uri": track['uri'],
            "master_metadata_track_name": track['name'],
            "master_metadata_album_artist_name": track['artists'][0]['name'],
            "master_metadata_album_album_name": track['album']['name'],
            "ms_played": track['duration_ms']
        }
    return None

def adjust_timestamp(ts, ms_played, reverse=False):
    dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
    delta = timedelta(milliseconds=ms_played)
    if reverse:
        new_dt = dt - delta
    else:
        new_dt = dt + delta
    return new_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def generate_entries(track_info, start_year, num_entries):
    start_date = datetime.strptime(f"{start_year}-01-01T08:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    max_date = datetime.strptime(f"{start_year}-12-25T23:59:59Z", "%Y-%m-%dT%H:%M:%SZ")
    
    template = {
        "ts": start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "username": "31dlfbglxnvsmqoixe74mzp64tay",
        "platform": "android",
        "ms_played": track_info["ms_played"],
        "conn_country": "FR",
        "ip_addr_decrypted": "8.8.8.8",
        "user_agent_decrypted": "unknown",
        "master_metadata_track_name": track_info["master_metadata_track_name"],
        "master_metadata_album_artist_name": track_info["master_metadata_album_artist_name"],
        "master_metadata_album_album_name": track_info["master_metadata_album_album_name"],
        "spotify_track_uri": track_info["spotify_track_uri"],
        "episode_name": None,
        "episode_show_name": None,
        "spotify_episode_uri": None,
        "reason_start": "trackdone",
        "reason_end": "trackdone",
        "shuffle": True,
        "skipped": False,
        "offline": False,
        "offline_timestamp": 1715445864,
        "incognito_mode": False
    }

    data = []
    last_ts = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    added_entries = 0

    for i in range(num_entries):
        new_entry = template.copy()
        new_entry["ts"] = last_ts
        new_entry["ms_played"] = track_info["ms_played"]
        current_time = datetime.strptime(last_ts, "%Y-%m-%dT%H:%M:%SZ")

        if current_time.time() < datetime.strptime("23:30:00", "%H:%M:%S").time() or current_time.time() > datetime.strptime("08:00:00", "%H:%M:%S").time():
            data.append(new_entry)
            added_entries += 1
        else:
            print(f"Horodatage {last_ts} non ajouté car il est entre 23:30 et 08:00")

        last_ts = adjust_timestamp(last_ts, new_entry["ms_played"])
        
        if datetime.strptime(last_ts, "%Y-%m-%dT%H:%M:%SZ").time() > datetime.strptime("23:30:00", "%H:%M:%S").time():
            next_day = datetime.strptime(last_ts, "%Y-%m-%dT%H:%M:%SZ").date() + timedelta(days=1)
            last_ts = f"{next_day}T08:00:00Z"
        
        if datetime.strptime(last_ts, "%Y-%m-%dT%H:%M:%SZ") > max_date:
            print(f"Atteint la date limite {last_ts}, arrêt des ajouts")
            break

    return data

questions = [
    inquirer.Text('track_name', message="Nom de la piste"),
    inquirer.Text('artist_name', message="Nom de l'artiste"),
    inquirer.Text('album_name', message="Nom de l'album"),
    inquirer.Text('start_year', message="Année de début", validate=lambda _, x: x.isdigit() and 1900 <= int(x) <= 2100),
    inquirer.Text('num_entries', message="Nombre d'entrées", validate=lambda _, x: x.isdigit())
]

answers = inquirer.prompt(questions)
track_name = answers['track_name']
artist_name = answers['artist_name']
album_name = answers['album_name']
start_year = answers['start_year']
num_entries = int(answers['num_entries'])

track_info = search_spotify_track(track_name, artist_name, album_name)

if track_info:
    entries = generate_entries(track_info, start_year, num_entries)

    file_name = f'Streaming_History_Audio_{start_year}.json'
    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(entries, file, ensure_ascii=False, indent=4)
    
    print(f"{len(entries)} nouvelles entrées ajoutées avec succès dans {file_name}.")
else:
    print("Piste introuvable sur Spotify. Veuillez vérifier les informations fournies.")
