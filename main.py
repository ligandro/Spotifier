import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.patheffects as path_effects
import matplotlib.font_manager as fm
from matplotlib.patches import Ellipse
import matplotlib.patches as mpatches
from matplotlib import cm
from highlight_text import fig_text, ax_text
from ast import literal_eval

from PIL import Image
import urllib
import os
import requests
import json
import argparse
from mplsoccer import PyPizza, add_image, FontManager

# -- For Logos and images
from matplotlib.transforms import Bbox
class BboxLocator:
    def __init__(self, bbox, transform):
        self._bbox = bbox
        self._transform = transform
    def __call__(self, ax, renderer):
        _bbox = self._transform.transform_bbox(self._bbox)
        return ax.figure.transFigure.inverted().transform_bbox(_bbox)
    
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import ast

# Function to add song image to table
def add_song_image(song_url, ax):
    '''
    '''
    song_icon = Image.open(urllib.request.urlopen(f'{song_url}'))
    ax.imshow(song_icon)
    ax.axis('off')
    return ax

# Function to shift text to next line if too long in table
def wrap_text(text, max_length=22):
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + 1 > max_length:
            lines.append(current_line)
            current_line = word
        else:
            current_line += " " + word if current_line else word

    lines.append(current_line)  # Add last line
    return "\n".join(lines)  


def main(client_id, client_secret, redirect_uri):
    scope = "user-read-recently-played"

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope
    ))

    recent_df = sp.current_user_recently_played()
    # Create a DataFrame from the list of items
    recent_df =  pd.json_normalize(recent_df["items"])

    # Add artist names
    recent_df["artist_name"] = recent_df["track.artists"].apply(lambda x: x[0]["name"] if isinstance(x, list) and x else None)


    # Check if the main_history.csv file exists
    if os.path.exists("data\main_history.csv"):
        # Read the existing main history
        df_main = pd.read_csv("data\main_history.csv")
        df_main["played_at"] = pd.to_datetime(df_main["played_at"])
    else:
        # Initialize df_main with recent_df if the file does not exist
        df_main = recent_df.copy()
        df_main["played_at"] = pd.to_datetime(df_main["played_at"])

    # Assuming recent_df is already defined and contains the new data
    recent_df["played_at"] = pd.to_datetime(recent_df["played_at"])

    # Get the latest timestamp in the main DataFrame
    last_played_at = df_main["played_at"].max() if not df_main.empty else pd.Timestamp.min

    # Filter the recent DataFrame to keep only new songs
    df_filtered = recent_df[recent_df["played_at"] > last_played_at]

    # Append new songs to the main DataFrame
    df_main = pd.concat([df_main, df_filtered], ignore_index=True)

    # Save the updated history to the CSV file
    df_main.to_csv('data\main_history.csv', index=False)




    # Create song counts dataframe 
    df_song_counts = df_main.groupby(["track.id", "track.name"]).size().reset_index(name="play_count")

    df_main = df_main.merge(df_song_counts, on=["track.id", "track.name"], how="left")

    df_main = df_main.drop_duplicates(subset=["track.id"], keep="first") # Remove duplicates


    # Convert string representations of lists to actual lists
    df_main["track.album.images"] = df_main["track.album.images"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    # Extract the URL where height is 300
    df_main["album_image"] = df_main["track.album.images"].apply(lambda x: next((img["url"] for img in x if img["height"] == 300), None))

    since_dt = df_main["played_at"].min().strftime("%d %b %Y") # Since date

    # Sort and add Rank for plotting
    df_main = df_main.sort_values(by="play_count",ascending=False)[:10].reset_index(drop=True)
    df_main["Rank"] = df_main.index+1
    df_plot = df_main[["Rank","album_image","track.name","track.album.name","artist_name","play_count"]]
    df_plot = df_plot[::-1]




    # Create Plot
    fig = plt.figure(figsize=(7,8), dpi=300)
    ax = plt.subplot()

    fig.set_facecolor('black')
    ax.patch.set_facecolor('black')

    nrows = df_plot.shape[0]
    ncols = df_plot.shape[1] 

    ax.set_xlim(0, ncols + 1)
    ax.set_ylim(-.65, nrows + 1)


    x0, y0 = ax.transAxes.transform((0, 0)) # lower left in pixels
    x1, y1 = ax.transAxes.transform((1, 1)) # upper right in pixes
    dx = x1 - x0
    dy = y1 - y0
    maxd = max(dx, dy)
    width = .26 * maxd / dx
    height = .81 * maxd / dy


    import warnings
    warnings.filterwarnings("ignore", message="findfont: Font family")

    # Add custom font
    custom_font_path = r"fonts\YatraOne-Regular.ttf"
    custom_font = fm.FontProperties(fname=custom_font_path)

    # Add custom font
    custom_font_path2 = r"fonts\Vercetti-Regular.ttf"
    custom_font2 = fm.FontProperties(fname=custom_font_path2)

    # Iterate row wise
    for y in range(0, nrows):

        bbox = Bbox.from_bounds(0.27, y - 0.4, 1.2, 0.8)
        logo_ax = fig.add_axes([0, 0, 0, 0], axes_locator=BboxLocator(bbox, ax.transData))
        add_song_image(df_plot['album_image'].iloc[y], logo_ax)

        ax_text(
            x=0.1, y=y,
            s=str(df_plot['Rank'].iloc[y]),
            size=9,color="white",weight='bold',
            ha='left', va='center', ax=ax, fontproperties=custom_font
        ) 
        ax_text(
            x=1.32, y=y,
            s=wrap_text(df_plot['track.name'].iloc[y]),
            size=9,color="white",weight='bold',
            ha='left', va='center', ax=ax, fontproperties=custom_font
        ) 

        ax_text(
            x=3.5, y=y,
            s=f"{wrap_text(df_plot['track.album.name'].iloc[y])}",
            size=9,color="white",weight='bold',
            ha='left', va='center', ax=ax, fontproperties=custom_font
        )

        ax_text(
            x=5.8, y=y,
            s=f"{df_plot['artist_name'].iloc[y]}",
            size=9,color="white",weight='bold',
            ha='left', va='center', ax=ax,fontproperties=custom_font
        )

        bbox = Bbox.from_bounds(7.15, y - .295, 1.8, .65)
        battery_ax = fig.add_axes([0, 0, 0, 0], axes_locator=BboxLocator(bbox, ax.transData))
        battery_ax.set_xlim(0,max(df_plot['play_count']))
        battery_ax.barh(y=.5, width=df_plot['play_count'].iloc[y], height=.3, alpha=.85)
        battery_ax.barh(y=.5, width=100, height=.5, alpha=.25, color='#41cf00', ec='black')
        text_ = battery_ax.annotate(
            xy=(df_plot['play_count'].iloc[y], .5),
            xytext=(5,0), family='STXihei',
            textcoords='offset points',color="white",
            text=f"{df_plot['play_count'].iloc[y]}",
            ha='left', va='center',fontproperties=custom_font2,
            size=8
        )
        text_.set_path_effects(
                    [path_effects.Stroke(linewidth=.15, foreground="white"), 
                    path_effects.Normal()]
                )
        battery_ax.set_axis_off()

    ax.set_axis_off()

    ax_text(
        x=0.185, y=nrows + .05,
        s='Rank',
        size=9,color="white",
        ha='center', va='center', ax=ax,fontproperties=custom_font,
        textalign='center', weight='bold'
    )
    ax_text(
        x=1.62, y=nrows + .05,
        s='Track',
        size=9,fontproperties=custom_font,color="white",
        ha='center', va='center', ax=ax,
        textalign='center', weight='bold'
    )
    ax_text(
        x=4.2, y=nrows + .05,
        s='Album',color="white",
        size=9,fontproperties=custom_font,
        ha='center', va='center', ax=ax,
        textalign='center', weight='bold'
    )

    ax_text(
        x=6.2, y=nrows + .05,
        s='Artist',
        size=9,fontproperties=custom_font,color="white",
        ha='center', va='center', ax=ax,
        textalign='center', weight='bold'
    )
    ax_text(
        x=8, y=nrows + .05,
        s='Play Count',color="white",
        size=9,fontproperties=custom_font,
        ha='center', va='center', ax=ax,
        textalign='center', weight='bold'
    )

    ax.plot([0, 10], [nrows - .35, nrows - .35], lw=1, color='white', zorder=3)

    ax.plot([10, 100], [nrows - .35, nrows - .35], lw=1, color='white', zorder=3)
    fig_text(
        x = 0.18, y = .858, 
        s = "Spotify Most Played Songs",
        va = "bottom", ha = "left",color="white",
        fontsize = 14,fontproperties=custom_font, weight = "bold"
    )
    fig_text(
        x = 0.18, y = .84, 
        s = f"viz by @ligandro22 | Since : {since_dt}",
        va = "bottom", ha = "left",
        fontsize = 7, color = "white",alpha=0.7, fontproperties=custom_font,
    )

    # Add spotify logo
    im1 = plt.imread(r"images\spoti.png")
    ax_image = add_image( im1, fig, left=0.112, bottom=0.828, width=0.064, height=0.064)
    ax.set_axis_off()

    plt.savefig("images\SpotiHist.jpg",dpi =500, bbox_inches='tight')



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Connect to Spotify API.")
    parser.add_argument("--client_id", required=True, help="Spotify API Client ID")
    parser.add_argument("--client_secret", required=True, help="Spotify API Client Secret")
    parser.add_argument("--redirect_uri", required=True, help="Spotify API Redirect URI")

    args = parser.parse_args()
    main(args.client_id, args.client_secret, args.redirect_uri)