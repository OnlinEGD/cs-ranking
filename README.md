<h1>CS2 ELO Ranking</h1>
A Python script that automatically updates an ELO ranking for CS2 teams based on match results from the <a href="https://www.pandascore.co">Pandascore</a> API. Match data is saved to a CSV file, and updates are triggered every 10 minutes using GitHub Actions.

<h2>Features</h2>

- Fetches finished CS2 matches from Pandascore (only tier S and A tournaments).

- Calculates ELO rating updates using the Elo algorithm (K=32).

- Adds new teams with a default ELO of 1000.

- Prevents reprocessing of already handled matches.

- Runs automatically every 10 minutes via GitHub Actions.

- Updatedes inactive teams ELO and sets negative value (After 180 days of inactivity).

<h2>GitHub Actions</h2>

- The workflow Run ELO Update Every 10 Minutes runs on a schedule (cron: */10 * * * *) and:

- Checks out the repository

- Installs dependencies

- Runs the Python script

- Commits and pushes any changes to ranking.csv and processed_matches.csv

<h2>File Structure</h2>

- script.py – the main script that fetches data and updates the rankings

- ranking.csv – current ELO rankings of teams

- processed_matches.csv – a list of match IDs that have already been processed

- .github/workflows/elo.yml – GitHub Actions workflow configuration

<h2>Notes</h2>

- Only finished CS2 matches from tier S and tier A tournaments are included.

- A match must have a status of finished to be processed.

- The ranking has been in force since 30th April 2025.

