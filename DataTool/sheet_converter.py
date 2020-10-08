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
    if i in ("Rank", "Player"):
         html += "<th class=l>" + i + "</th>"
         
    else:
        html += "<th>" + i + "</th>"

html += "</tr>"

rank = 1

for line in table:
    html += "\n\t<tr><td class=l>" + str(rank) + "</td>"

    column = 1
    
    for entry in line:
        if entry:
            if column == 1: # A name
                if rank == 1:   html += "<td class=n1>" + entry + "</td>"
                elif rank == 2:   html += "<td class=n2>" + entry + "</td>"
                elif rank == 3:   html += "<td class=n3>" + entry + "</td>"
                else:   html += "<td class=n>" + entry + "</td>"

            elif column == 2:   html += "<td class=w>" + entry + "</td>"
            elif column == 3:   html += "<td class=z>" + entry + "</td>"
            elif column in (4,7):   html += "<td class=r>" + entry + "</td>"
                
            else:   html += "<td>" + entry + "</td>"

        column += 1
        
    html += "</tr>"

    rank += 1

html += "\n</table>\n\n<p class=dis>" + "Last updated " +\
        time.strftime("%Y-%m-%d") + ".</p>"

html = html.replace("<tr><td>1</td><td>",
                    "<tr><td>1</td><td class=n1>", 1)
html = html.replace("<tr><td>2</td><td>",
                    "<tr><td>2</td><td class=n2>", 1)
html = html.replace("<tr><td>3</td><td>",
                    "<tr><td>3</td><td class=n3>", 1)

print(html)


#soup = bs4.BeautifulSoup(html, 'html.parser')
#print(soup.prettify())
