import pandas as pd 
import requests
from datetime import datetime
import os

K = 32

df = pd.read_csv("ranking.csv", sep=";", encoding="utf-8")

processed_matches_file = "processed_matches.csv"
if not os.path.exists(processed_matches_file):
    processed_matches_df = pd.DataFrame(columns=["match_id"])
    processed_matches_df.to_csv(processed_matches_file, index=False)
else:
    processed_matches_df = pd.read_csv(processed_matches_file)

PANDASCORE_TOKEN = os.getenv('PANDASCORE_TOKEN')

if PANDASCORE_TOKEN is None:
    raise ValueError("Token Pandascore nie jest ustawiony w zmiennych środowiskowych!")

URL = f"https://api.pandascore.co/matches?sort=-modified_at&token={PANDASCORE_TOKEN}"


response = requests.get(URL)

def update_elo(team_a, team_b, score_a=2, score_b=1):
    global df

    print(f"Aktualizuję ranking dla meczu: {team_a} vs {team_b}")

    for team in [team_a, team_b]:
        if team not in df["Team"].values:
            new_team = pd.DataFrame([{"Team": team, "Elo": 1000}])
            df = pd.concat([df, new_team], ignore_index=True)
            print(f"Dodano drużynę {team} do rankingu z początkowym ELO 1000.")

    R_A = df.loc[df["Team"] == team_a, "Elo"].values[0]
    R_B = df.loc[df["Team"] == team_b, "Elo"].values[0]

    E_A = 1 / (1 + 10 ** ((R_B - R_A) / 400))
    E_B = 1 / (1 + 10 ** ((R_A - R_B) / 400))

    S_A = 1 if score_a > score_b else 0
    S_B = 1 if score_b > score_a else 0

    R_A_new = R_A + K * (S_A - E_A)
    R_B_new = R_B + K * (S_B - E_B)

    df.loc[df["Team"] == team_a, "Elo"] = round(R_A_new)
    df.loc[df["Team"] == team_b, "Elo"] = round(R_B_new)

    df['Placement'] = df['Elo'].rank(ascending=False, method='min').astype(int)

    df.to_csv("ranking.csv", sep=";", index=False, encoding="utf-8")
    
    print(f"Nowy ranking: {team_a} - {round(R_A_new)}, {team_b} - {round(R_B_new)}")
    print(f"Ranking zapisany do pliku ranking.csv.")


if response.status_code == 200:
    matches = response.json()
    
    for match in matches:
        match_id = match["id"]

        if match_id in processed_matches_df["match_id"].values:
            print(f"\nMecz {match['name']} (ID: {match_id}) już został przetworzony. Pomijamy.")
            continue

        if 'videogame' in match and match['videogame']['name'] == "Counter-Strike":
            if 'serie' in match and 'full_name' in match['serie']:
                tournament_full_name = match['serie']['full_name']
                
                if match['tournament']['tier'] in ["s", "a"]:
                    if 'status' in match and match['status'] == 'finished':
                        print(f"\nMecz zakończony: {match['name']} (ID: {match_id})")

                        if 'scheduled_at' in match:
                            match_date = match['scheduled_at']
                            match_datetime = datetime.strptime(match_date, '%Y-%m-%dT%H:%M:%SZ')
                            formatted_date = match_datetime.strftime('%d-%m-%Y %H:%M:%S')
                            print(f"Data meczu: {formatted_date}")
                        
                        if len(match['opponents']) >= 2:
                            team_a_name = match['opponents'][0]['opponent']['name']
                            team_b_name = match['opponents'][1]['opponent']['name']
                            
                            score_a = 0
                            score_b = 0
                            for result in match['results']:
                                if result['team_id'] == match['opponents'][0]['opponent']['id']:
                                    score_a = result['score']
                                elif result['team_id'] == match['opponents'][1]['opponent']['id']:
                                    score_b = result['score']
                            
                            update_elo(team_a_name, team_b_name, score_a, score_b)

                            print(f"Match Name: {match['name']}")
                            print(f"Tournament Name: {match['tournament']['name']}")
                            print(f"Scheduled Date: {formatted_date}")
                            print(f"Team A: {team_a_name} - Score A: {score_a}")
                            print(f"Team B: {team_b_name} - Score B: {score_b}")
                            print(f"Tournament Full Name: {tournament_full_name}")
                            print(f"Tournament tier: {match['tournament']['tier']}")
                            print(f"Placement of {team_a_name}: {df.loc[df['Team'] == team_a_name, 'Placement'].values[0]}")
                            print(f"Placement of {team_b_name}: {df.loc[df['Team'] == team_b_name, 'Placement'].values[0]}")
                            print('-' * 30)

                            processed_matches_df = pd.concat([processed_matches_df, pd.DataFrame([{"match_id": match_id}])], ignore_index=True)
                            processed_matches_df.to_csv(processed_matches_file, index=False)
                        else:
                            print(f"Nie wystarczająca liczba drużyn w meczu: {match['name']}")
                            print('-' * 30)
                    else:
                        print(f"\nMecz {match['name']} jeszcze się nie zakończył.")
                        print(f"Scheduled Date: {match['scheduled_at']}")
                        print('-' * 30)
else:
    print(f"Error: {response.status_code}")
