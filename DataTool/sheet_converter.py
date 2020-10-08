import bs4, time

with open("input.txt") as f:
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

html = "<table>"

html += "\n\t<tr>"

for i in ("Rank", "Player", "Wins", "Losses", "Games Played",
          "Score", "Win Rate", "Rating"):
    html += "<th>" + i + "</th>"

html += "</tr>"

rank = 1

for line in table:
    html += "\n\t<tr><td>" + str(rank) + "</td>"
    for entry in line:
        if entry:   html += "<td>" + entry + "</td>"
        
    html += "</tr>"

    rank += 1

html += "\n</table>\n\n<p>" + "Last updated " + time.strftime("%Y-%m-%d") + ".</p>"

print(html)


#soup = bs4.BeautifulSoup(html, 'html.parser')
#print(soup.prettify())
