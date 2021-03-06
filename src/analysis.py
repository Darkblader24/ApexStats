
import numpy as np
import matplotlib.pyplot as plt
import os

# to convert time survived to seconds
import datetime
import time


from scipy.optimize import curve_fit
from scipy.special import gamma

# 0 to disable
use_last_n_games = 50

# empty list to disable
show_only_group_size = []
show_only_legend = []


def filter_stat(filter, stats):
    mask = [x in filter for x in stats]
    return stats[mask]


def main_graphs():

    filename = "Apex Stats.txt"
    desktoppath = os.path.join(os.path.join(os.environ["USERPROFILE"]), "Desktop")
    desktoppath = os.path.join(desktoppath, filename)

    desktoppath = "../output/Apex Stats.txt"

    season, group_size, temporary_time_survived, legend, damage, kills, revives, respawns, placement = np.genfromtxt(desktoppath, comments="\"", unpack=True, dtype="str", delimiter="\t", skip_header=True)

    season = season[1:].astype(int)
    group_size = group_size[1:].astype(int)
    temp_time = (time.strptime(temporary_time_survived[i], "%M:%S") for i in range(1, len(temporary_time_survived)))
    temp_seconds_survived = (datetime.timedelta(minutes=x.tm_min, seconds=x.tm_sec).total_seconds() for x in temp_time)
    seconds_survived = np.array([])
    for x in temp_seconds_survived:
        seconds_survived = np.append(seconds_survived, float(x))
    legend = legend[1:]
    damage = damage[1:].astype(int)
    kills = kills[1:].astype(int)
    revives = revives[1:].astype(int)
    respawns = respawns[1:].astype(int)
    placement = placement[1:].astype(int)

    if use_last_n_games != 0:
        if use_last_n_games > len(season):
            raise IndexError("There are a maximum of " + str(len(season)) + " Games available.")
        n = use_last_n_games
        season = season[-n:]
        group_size = group_size[-n:]
        seconds_survived = seconds_survived[-n:]
        legend = legend[-n:]
        damage = damage[-n:]
        kills = kills[-n:]
        revives = revives[-n:]
        respawns = respawns[-n:]
        placement = placement[-n:]

    if show_only_group_size:
        mask = [x in show_only_group_size for x in group_size]
        season = season[mask]
        group_size = group_size[mask]
        seconds_survived = seconds_survived[mask]
        legend = legend[mask]
        damage = damage[mask]
        kills = kills[mask]
        revives = revives[mask]
        respawns = respawns[mask]
        placement = placement[mask]

    if show_only_legend:
        mask = [x in show_only_legend for x in legend]
        season = season[mask]
        group_size = group_size[mask]
        seconds_survived = seconds_survived[mask]
        legend = legend[mask]
        damage = damage[mask]
        kills = kills[mask]
        revives = revives[mask]
        respawns = respawns[mask]
        placement = placement[mask]

    if len(season) == 0:
        print("No games to evaluate!")
        return -1

    if len(season) <= 10:
        print("Not enough games to evaluate!")
        return -1


    win = placement == 1
    solo = group_size == 1

    unique, counts = np.unique(solo, return_counts=True)

    groupsizelabels = []
    for played_solo in unique:
        if played_solo:
            groupsizelabels.append("Solo")
        else:
            groupsizelabels.append("Group")


    plt.figure(figsize=(7, 7))
    plt.pie(counts, labels=groupsizelabels, explode=[0.1] * len(counts), autopct="%1.0f%%")
    plt.title("Playing solo versus in a Group")
    plt.show()

    playtimes = {}
    for l in legend:
        mask = legend == l
        pt = seconds_survived[mask]
        playtimes[l] = sum(pt)

    print("Total Survival Times:")
    for key, value in playtimes.items():
        if len(key) < 7:
            print("{value1:s}:\t\t{value2:.0f}".format(value1=key, value2=value))
        else:
            print("{value1:s}:\t{value2:.0f}".format(value1=key, value2=value))



    plt.figure(figsize=(7, 7))
    plt.pie(playtimes.values(), labels=playtimes.keys(), explode=[0.1] * len(playtimes.values()), autopct="%1.0f%%")
    plt.title("Playtime by Legend")
    plt.show()

    unique, counts = np.unique(legend, return_counts=True)

    plt.figure(figsize=(7, 7))
    plt.pie(counts, labels=unique, explode=[0.1] * len(counts), autopct="%1.0f%%")
    plt.title("Number of Games Played by Legend")
    plt.show()

    unique, counts = np.unique(kills, return_counts=True)

    popt, pcov = curve_fit(poisson, unique, counts)

    print("Expected Kills Per Game: ({value1:f} +/- {value2:f})".format(value1=popt[1], value2=np.sqrt(pcov[1][1])))

    plt.bar(unique, counts)
    x = np.linspace(min(unique) - 1, max(unique) + 1)
    plt.plot(x, poisson(x, *popt), label="Fit", color="orange")
    plt.xlabel("Kills")
    plt.ylabel("Frequency")
    plt.title("Kill Count per Game")
    plt.show()

    unique, counts = np.unique(revives, return_counts=True)

    plt.bar(unique, counts)
    plt.xlabel("Revives")
    plt.ylabel("Frequency")
    plt.title("Revive Count per Game")
    plt.show()

    unique, counts = np.unique(respawns, return_counts=True)

    plt.bar(unique, counts)
    plt.xlabel("Respawns")
    plt.ylabel("Frequency")
    plt.title("Respawn Count per Game")
    plt.show()


    # TODO: Overlay proper poisson function on this
    # specify number of bins here
    numbins = 20
    # binranges = np.array([i * (max(damage) - min(damage)) / numbins for i in range(0, numbins)])
    # histcounts = np.array([0] * len(binranges))
    # for x in damage:
    #     sorted_in = False
    #     for i in range(1, len(binranges)):
    #         if x < binranges[i]:
    #             histcounts[i - 1] += 1
    #             sorted_in = True
    #             break
    #     if not sorted_in:
    #         histcounts[len(histcounts) - 1] += 1
    #
    #
    # print(binranges)
    # print(histcounts)

    # popt, pcov = curve_fit(poisson, binranges[0:12], histcounts[0:12], p0=[20, 200])

    # print("Expected Damage per Game: ({value1:f} +/- {value2:f})".format(value1=popt[1], value2=np.sqrt(pcov[1][1])))

    plt.hist(damage, bins=numbins, rwidth=0.95)
    # x = np.linspace(min(binranges) - 50, max(binranges) + 50)
    # plt.plot(x, poisson(x, *popt), label="Fit", color="orange")
    # plt.scatter(binranges, histcounts, color="orange")
    plt.xlabel("Damage")
    plt.ylabel("Frequency")
    plt.title("Damage dealt per Game")
    plt.show()

    unique, counts = np.unique(placement, return_counts=True)

    plt.bar(unique, counts)
    plt.xlabel("Placement")
    plt.ylabel("Frequency")
    plt.title("Placement Distribution")
    plt.xlim(21, 0)
    plt.show()

    # placement by time
    x = range(0, len(placement))

    popt, pcov = curve_fit(linear, x, placement)

    plt.scatter(x, placement)
    plt.plot(x, linear(x, *popt), label="Trend", color="orange")
    plt.xlabel("Game")
    plt.ylabel("Placement")
    plt.title("Placement by Game")
    plt.ylim(21, 0)
    plt.legend()
    plt.show()


    # specify number of bins here
    numbins = 20

    plt.hist(seconds_survived, bins=numbins, rwidth=0.95)
    plt.xlabel("Time Survived (s)")
    plt.ylabel("Frequency")
    plt.title("Time survived per Game")
    plt.show()



    unique, counts = np.unique(win, return_counts=True)

    plt.figure(figsize=(7, 7))
    plt.pie(counts, labels=["No Win", "Win"], explode=[0.1] * len(counts), autopct="%1.0f%%")
    plt.title("Win Percentage")
    plt.show()

    popt, pcov = curve_fit(linear, kills, damage)
    popt2, pcov2 = curve_fit(linear_zero, kills, damage)

    print("Damage per Kill (with zero-kill dmg): ({value1:f} +/- {value2:f})".format(value1=popt[0], value2=np.sqrt(pcov[0][0])))
    print("Damage per Kill (without zero-kill dmg): ({value1:f} +/- {value2:f})".format(value1=popt2[0], value2=np.sqrt(pcov2[0][0])))
    print("Zero-Kill-Damage: ({value1:f} +/- {value2:f})".format(value1=popt[1], value2=np.sqrt(pcov[1][1])))

    x = np.linspace(0, max(kills))

    plt.scatter(kills, damage)
    plt.plot(x, linear(x, *popt), label="Fit", color="orange")
    plt.plot(x, linear_zero(x, *popt2), label="Fit", color="orange")
    plt.xlabel("kills")
    plt.ylabel("damage")
    plt.title("damage By kills")
    plt.show()

    return 0


def gaussian(x, A, mu, sig):
    return A / (np.sqrt(2 * np.pi) * sig) * np.exp(-(x-mu) ** 2 / (2 * sig ** 2))


def poisson(x, A, mu):
    return A * np.exp(-mu) * mu ** x / gamma(x + 1)


def linear(x, a, b):
    return a * x + b


def linear_zero(x, c):
    return c * x
