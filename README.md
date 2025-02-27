# Spotifier

<p align="center">
  <img width="100%" src="./images/sample.jpg"> &nbsp &nbsp
</p>

## Overview
Simple Python script that generates a table of your song listening history using data from **Spotipy API**.

## Features
Data Integration: Automatically fetches and integrates your Spotify listening history.
Visualization: Generates visualization to display your listening habits over time.

## Installation 

### 1. Clone the Repository:
```bash
git clone https://github.com/ligandro/Spotifier.git
cd ligandro/Spotifier.git 
```

### 2. Set Up a Virtual Environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```
### 3. Install Dependencies:

```bash
pip install -r requirements.txt
```


## How It Works
The script uses the Spotipy API to get your recent song listening data. It allows us to get only the latest 50 so we have set up a csv file to continuously store the data. This means you will have to routinely run the script to keep your data accurate. We then use Matplotlib to plot your top 10 most listened songs.

## Usage
Run the Script:
```bash
python main.py --client_id "your_client_id" --client_secret "your_client_secret" --redirect_uri "your_redirect_uri"
```
Client ID, Client Secret can be obtained from Spotify Developers website.  You cam use this video as reference https://youtu.be/0fhkkkRuUxw

##  Contributing and Contact
Contributions are welcome! This project was mainly inspired by https://receiptify.herokuapp.com/#google_vignette. I don't know how to set up the web login for each user and also getting the full listening history yet. If you have any questions or suggestions, feel free to open an issue or contact me at my twitter. 

## License
MIT License

