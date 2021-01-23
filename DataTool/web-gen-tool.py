# (c) 2020 Jesse Forgione

import bs4, glob, json, os, time

SEASON_TEMPLATE = """<!DOCTYPE html>
<html>
<head><title>AEGIS League - {$EventName$}</title>
<meta charset="utf-8" />
<link rel="stylesheet" href="/AEGIS/styles.css?version=2" /></head>
	
<body><h1>AEGIS League {$EventName$} {$HeaderText$}</h1>
<p>{$BodyText$}</p>

<h2>{$EventName$} Rankings</h2>
{$EventTable$}
<p class="dis">Last updated %DATE%.</p>
<p><a href="/AEGIS/index.html">Return to Main Page</a></p>
</body>
</html>
""".replace("%DATE%", time.strftime("%Y-%m-%d"))

PLAYER_TEMPLATE = """<!DOCTYPE html>
<html>
<head><title>AEGIS League - {$PlayerName$}</title>
<meta charset="utf-8" />
<link rel="stylesheet" href="/AEGIS/styles.css?version=2" /></head>
	
<body><h1>{$PlayerName$}'s Stats</h1>
<p>{$PlayerStats$}</p>

<h2>Rankings</h2>
{$PlayerTable$}
<p class="dis">Last updated %DATE%.</p>
<p><a href="/AEGIS/index.html">Return to Main Page</a></p>
</body>
</html>
""".replace("%DATE%", time.strftime("%Y-%m-%d"))

def getrank(rank):
    if rank > 10 and rank < 20: return str(rank) + "th"
    elif str(rank)[-1] == '1':   return str(rank) + "st"
    elif str(rank)[-1] == '2':   return str(rank) + "nd"
    elif str(rank)[-1] == '3':   return str(rank) + "rd"
    else:   return str(rank) + "th"

def make_file_name(dir, name):
    return dir.lower() + os.path.sep + name.replace(" ",'-').lower() + '.html'

# Player table =======================

def gen_player_table(playername):
    html = "<table>\n<tr>"

    # Header row
    for i in ("Event", "Rank", "Wins", "Losses", "Games Played", "Win Rate",
              "Score"):
        if i in ("Event", "Rank"): html += "<th class=l>" + i + "</th>"         
        else:   html += "<th>" + i + "</th>"
    html += "</tr>"

    # Table rows
    for event in PLAYER_RANKS[playername]:
        ed = PLAYER_RANKS[playername][event]
        html += "\n<tr>"
        # Event name
        s = "<td class=l><a href={$lnk$}>{$name$}</a></td>".replace(
            "{$lnk$}", "/AEGIS/events/"+event.lower().replace(" ", "-")+".html")
        html += s.replace("{$name$}", event)
        # Place
        html += "<td class=l>" + getrank(ed[0]) + "</td>"
        # Wins
        html += "<td class=w>" + ed[2] + "</td>"
        # Losses
        html += "<td class=z>" + ed[3] + "</td>"
        # Games Played
        html += "<td class=l>" + ed[4] + "</td>"
        # Win Rate
        html += "<td>" + ed[5] + "</td>"
        # Score
        html += "<td>" + ed[6] + "</td>"
        
        html += "</td></tr>"

    html += "\n</table>"
    
    return html

# Season table =======================

def gen_season_table(data, eventname):
    html = "<table>\n<tr>"

    # Header row
    for i in ("Rank", "Player", "Wins", "Losses", "Games Played", "Win Rate",
              "Score"):
        if i in ("Rank", "Player"): html += "<th class=l>" + i + "</th>"         
        else:   html += "<th>" + i + "</th>"
    html += "</tr>"

    # Number crunching
    players = []

    keys = list(data)
    keys.remove(" _$METADATA$_ ")
    
    for player in keys:
        wins = data[player]['wins']
        losses = data[player]['losses']
        games = wins + losses

        rate = wins / games
        
        score = round(rate * wins, 2)
        rate = round(rate*100)    # make percentage

        if games > 1:
            players.append([score, player, str(wins), str(losses), str(games),
                            str(rate)+'%','{:.2f}'.format(score)])

    players.sort(reverse=True)

    # Generate table rows
    rank = 0

    prevrate = -1    # for tie-checking
    ties = 0

    for pd in players:
        if pd[0] == prevrate:   # Tie
            ties += 1
        elif ties:  # There was a tie but now back to normal
            rank += ties + 1
            ties = 0
        else:   # Normal
            rank += 1

        prevrate = pd[0]
        pd[0] = rank

        # Generate html table
        column = 0
        html += "\n<tr>"
        
        for entry in pd:
            if column == 0: html += "<td class=l>" + getrank(rank) + "</td>"
            elif column == 1: # A name
                if rank == 1:   clas = 'n1'
                elif rank == 2:   clas = 'n2'
                elif rank == 3:   clas = 'n3'
                else:   clas = 'n'

                s = "<td><a class={$cl$} href={$lnk$}>" + entry + "</a></td>"

                url = "/AEGIS/player/" + entry.lower().replace(" ","-")+'.html'
                s = s.replace("{$cl$}", clas).replace("{$lnk$}", url)

                html += s

            elif column == 2:   html += "<td class=w>" + entry + "</td>"
            elif column == 3:   html += "<td class=z>" + entry + "</td>"
            elif column in [4]:   html += "<td class=r>" + entry + "</td>"
                
            else:   html += "<td>" + entry + "</td>"

            column += 1
            
        html += "</tr>"

        # Add rank for easy lookup
        global PLAYER_RANKS
        if pd[1] in PLAYER_RANKS:
            PLAYER_RANKS[pd[1]][eventname] = pd
        else:
            PLAYER_RANKS[pd[1]] = {}
            PLAYER_RANKS[pd[1]][eventname] = pd

    html += "</table>"

    return html


VERBOSE = 0

PLAYERS = {}
SEASONS = {}
TOURNEYS = {}

PLAYER_RANKS = {}
GLOBAL_RANKS = {}

# Get all the data from league seasons
for season in glob.glob("seasons" + os.path.sep + "*.txt"):
    sname = season.replace("seasons" + os.path.sep, "").replace(".txt","")
    print("Loading", sname)
    
    with open(season) as f:
        data = f.read()
        data, meta = data.split("\n\n")

    table = {}

    # Parse metadata
    md = meta.split("\n")
    meta = {}

    meta["header"] = md[0]
    meta["body"] = md[1]
    table[" _$METADATA$_ "] = meta

    for line in data.split("\n"):
        if VERBOSE: print(line)

        # Transform into a dict
        row = {}
        form = ["player", 'wins', 'losses']
        
        for entry in line.split('\t'):
            if form[0] in ('wins', 'losses'):
                try:    row[form.pop(0).lower()] = int(entry)
                except: row[form.pop(0).lower()] = float(entry)
            else:
                name = entry
                form.pop(0)

        if row['wins'] > 0 or row['wins'] + row['losses'] > 2:
            table[name] = row
        if VERBOSE: print(row)


        # Update the player's listing
        listing = {
            'wins': row['wins'],
            'losses': row['losses'],
            }

        if name in PLAYERS:
            PLAYERS[name][sname] = listing
                               
        else:
            PLAYERS[name] = {sname: listing}

    SEASONS[sname] = table
    
    if VERBOSE: print(table)

if VERBOSE:
    print(PLAYERS)
    print()
    print(SEASONS)

# Create event pages
for event in SEASONS:
    ed = SEASONS[event]
    meta = ed[" _$METADATA$_ "]

    html = SEASON_TEMPLATE.replace("{$EventName$}", event).replace(
        "{$EventTable$}", gen_season_table(ed, event)).replace(
            "{$HeaderText$}", meta['header']).replace(
                "{$BodyText$}", meta['body'])

    fn = make_file_name("events", event)
    with open(fn, 'w') as f:
        print("Writing", fn)
        f.write(html)

    # Make index page
    if event == "Season 3":
        print("Writing index.html")

        with open("index-template.html", 'r') as f:
            index = f.read().replace("%DATE%", time.strftime("%Y-%m-%d"))

            if False:   # Write index?
                index = index.replace("<!-- TABLE -->",
                                      gen_season_table(ed, event))

        with open('index.html', 'w') as f:
            f.write(index)

# Get player global ranks
grates = []

for player in PLAYERS:
    pd = PLAYERS[player]

    wins = 0
    losses = 0
    for i in pd:
        wins += pd[i]['wins']
        losses += pd[i]['losses']

    grates.append([round(wins**2 / (wins + losses), 2), player])

grates.sort(reverse=True)

rank = 0
prevrate = -1    # for tie-checking
ties = 0

for i in grates:
    if i[0] == prevrate:   # Tie
        ties += 1
    elif ties:  # There was a tie but now back to normal
        rank += ties + 1
        ties = 0
    else:   # Normal
        rank += 1

    prevrate = i[0]

    GLOBAL_RANKS[i[1]] = getrank(rank)

# Create player pages
names = []

for player in PLAYERS:
    pd = PLAYERS[player]

    wins = 0
    losses = 0
    for i in pd:
        wins += pd[i]['wins']
        losses += pd[i]['losses']

    stats = "Games Played: " + str(round(wins + losses)) + "<br />"
    stats += "Wins: " + str(wins) + "<br />"
    stats += "Losses: " + str(losses) + "<br />"
    stats += "Win Rate: " + str(round(wins*100 / (wins + losses))) + "%<br />"
    stats += "Overall Score: {:.2f} <br /><br />".format(
        round(wins**2 / (wins + losses), 2))

    stats += "Global Rank: " + GLOBAL_RANKS[player]

    if player in PLAYER_RANKS:
        html = PLAYER_TEMPLATE.replace("{$PlayerName$}", player).replace(
            "{$PlayerStats$}", stats).replace("{$PlayerTable$}",
                                              gen_player_table(player))

    fn = make_file_name("player", player)

    if fn in names: input(fn)
    else:   names.append(fn)
    
    with open(fn, 'w') as f:
        print("Writing", fn)
        f.write(html)

input("\nDone")
