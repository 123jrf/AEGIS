import bs4, glob, os, time

FORMAT1 = ("Rank", "Player", "Wins", "Losses", "Games Played", "Score",
           "Win Rate", "Rating")

PLAYERS = {}
SEASONS = {}

for season in glob.glob("seasons" + os.path.sep + "*.txt"):
    print(season)
    
    with open(season) as f:
        data = f.read()

    table = []

    for line in data.split("\n"):
        print(line)
        row = []
        
        for entry in line.split('\t'):
            row.append(entry)

        table.append(row)
        print(row)

    print(table)



