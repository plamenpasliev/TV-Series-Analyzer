import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as col
import matplotlib
import seaborn as sns
import requests

from omdb import OMDBClient
from PIL import Image
from io import BytesIO

# returns poster and information about the series
def get_data(title="Game of Thrones"):
    client = OMDBClient(apikey="cc71ac81")
    client.set_default("tomatoes", True)

    xml_content = client.get(title=title)

    response = requests.get(xml_content["poster"])
    img = Image.open(BytesIO(response.content))
    img.save("static/{}.png".format(title.lower()), format="png")

    return xml_content


def get_ratings(title="Game of Thrones"):

    try:
        # check if we already have the ratings of the listing
        data = np.load("data/{}.npy".format(title.lower()))
        print("Loaded data from disk")
        return data, title
    except:
        client = OMDBClient(apikey="cc71ac81")
        client.set_default("tomatoes", True)
        # ratings for season 1
        xml_content = client.get(title=title, season=1)
        num_episodes = len(xml_content["episodes"])

        # total number of seasons
        total_seasons = int(xml_content["total_seasons"])
        print("Total seasons: {}".format(total_seasons))

        list = []
        listoflists = []

        for item in xml_content["episodes"]:
            list.append(item["imdb_rating"])
        listoflists.append(list)
        print(listoflists)

        # get the ratings of other seasons
        for i in range(2, total_seasons + 1):
            list = []
            xml_content = client.get(title=title, season=i)
            for item in xml_content["episodes"]:
                list.append(item["imdb_rating"])
            listoflists.append(list)

        print(listoflists)
        maxlen = 0
        for item in listoflists:
            if len(item) > maxlen:
                maxlen = len(item)

        for item in listoflists:
            while len(item) < maxlen:
                item.append(None)

        data = np.array(listoflists).transpose()
        np.place(data, data == "N/A", None)
        print(data)
        data = data.astype(np.float)
        print("Loaded data from omdb")
        np.save("data/{}".format(title.lower()), data)
        return data, title


def get_colors(rating_data):
    cmap = matplotlib.cm.get_cmap("seismic")
    norm = matplotlib.colors.Normalize(
        vmin=np.nanmin(rating_data), vmax=np.nanmax(rating_data)
    )

    colors = []
    for item in rating_data:
        for i in item:
            if not np.isnan(i):
                colors.append(col.to_hex(cmap(norm(i))))
            else:
                colors.append("#FFFFFF")

    return colors


def get_xy_labels(rating_data):
    # adding season (column) labels
    collabels = []
    i = 1
    for item in rating_data[0]:
        collabels.append("Season {}".format(i))
        i = i + 1

    # episode (row) labels
    rowlabels = []
    i = 1
    for item in rating_data:
        rowlabels.append("Episode {}".format(i))
        i = i + 1

    return collabels, rowlabels


def plot_matrix(rating_data, colors, title="Game of Thrones"):
    sns.set()
    collabels, rowlabels = get_xy_labels(rating_data)

    fig = plt.figure(figsize=(len(collabels), len(rowlabels)))

    ax = fig.add_subplot(1, 1, 1)

    # plotting table
    table = plt.table(
        cellText=rating_data,
        cellColours=np.array(colors).reshape(rating_data.shape),
        colLabels=collabels,
        rowLabels=rowlabels,
        loc="best",
    )

    # hide nans
    cells = table.get_celld()
    for i in range(rating_data.shape[0] + 1):
        for j in range(rating_data.shape[1]):
            if cells[i, j].get_text().get_text() == "nan":
                cells[i, j].set_visible(False)

    table.set_fontsize(14)
    table.scale(1, 4)
    plt.tight_layout()
    ax.axis("off")
    plt.savefig("static/{}_rating_matrix".format(title.lower()), bbox_inches="tight")
    plt.close()


def plot_rating_per_season(data, title):
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(1, 1, 1)

    mean_ratings_per_season = np.nanmean(data, axis=0)
    seasonlabels, episodelabels = get_xy_labels(data)

    sns.lineplot(seasonlabels, mean_ratings_per_season, markers=True)

    ax.set_ylabel("IMDB Rating")
    ax.set_title("Mean episode rating per season")
    plt.savefig(
        "static/{}_rating_per_season".format(title.lower()), bbox_inches="tight"
    )
    plt.close()


def plot_scattered_ratings_per_season(data, title):
    seasonlabels, episodelabels = get_xy_labels(data)
    if len(seasonlabels) == 1:
        return 1

    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot(1, 1, 1)

    results = []
    for i in range(len(seasonlabels)):
        for j in range(len(data)):
            results.append((i, data[j, i]))

    results = pd.DataFrame(results)

    ax = sns.regplot(results[0], results[1], order=2)
    ax.set_xticks(np.arange(len(seasonlabels)))
    ax.set_xticklabels(seasonlabels)
    ax.set_ylabel("IMDB Score")
    ax.set_xlabel("")
    ax.set_title("Ratings per season")
    plt.savefig(
        "static/{}_scattered_rating_per_season".format(title.lower()),
        bbox_inches="tight",
    )
    plt.close()
