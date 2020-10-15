#!//Library/Frameworks/Python.framework/Versions/3.8/bin/python3
# -*- coding: utf-8 -
from bs4 import BeautifulSoup as soup
import requests
from prettytable import PrettyTable
import sys

class Main:
    def __init__(self):
        self.scraper = Scraper()
        self.url = "https://www.skysports.com/"
        self.league = ""    
        self.leaguetitle = ""
        self.year = ""
 
    def setLeagueTitle(self):

        if str(self.league) == 'premier-league':
            self.leaguetitle = 'Premier League'
        elif str(self.league) == 'la-liga':
            self.leaguetitle = 'La Liga'
        elif str(self.league) == 'bundesliga':
            self.leaguetitle = 'Bundesliga'
        elif str(self.league) == 'serie-a':
            self.leaguetitle = 'Serie A'
        elif str(self.league) == 'eredivisie':
            self.leaguetitle = 'Eredivisie'
        elif str(self.league) == 'ligue-1':
            self.leaguetitle = 'Ligue 1'
        elif str(self.league) == 'championship':
            self.leaguetitle = 'Championship'
        elif str(self.league) == 'champions-league':
            self.leaguetitle = 'Champions League'


    def scrape(self):

        if len(sys.argv) > 1:
            self.year = sys.argv
            self.year.pop(0)
            self.year = "20" + str((str(self.year)[2]) + str(self.year)[3])
            secondyear = int(str(self.year)[2] + str(self.year)[3]) + 1
            print(secondyear)


        league = input("Hvilken liga vil du se tabell for?\n")
        self.league = self.determineLeague(league)
        self.url = self.url + self.league + "-table/" + self.year

        page_html = self.scraper.scrapePage(self.url)
        page_soup = soup(page_html, "html.parser")
        
        tables = page_soup.findAll("table", {"class":{"standing-table__table"}})

        if not len(tables):
            print("Table not found")
            return

        self.setLeagueTitle()

        tabledirectory = {}

        tablenum = 0

        for x in range(0, len(tables)):
            tabledirectory["t{0}".format(x)]=PrettyTable()

        # Key information on the bottom 
        key_info = page_soup.find("div", {"class":"standing-table__supplementary"})

        for table in tables:

            t = tabledirectory["t" + str(tablenum)]

            t.field_names = ['#', 'Team', 'P', 'W', 'D', 'L', 'F', 'A', 'GD', 'Pts', 'Form[W,D,L]']
            tabletitle = table.findAll("caption", {"class":"standing-table__caption"})
            t.title = tabletitle[0].text.strip()
            team = table.findAll("td", {"class":"standing-table__cell standing-table__cell--name"})
            teamlist = []
            rest = table.findAll("td", {"class":"standing-table__cell"})
            form = table.findAll("div", {"class":"standing-table__form"})


            jump = 11
            posindex = 0
            playedindex = 2
            winindex = 3
            drawindex = 4
            lossindex = 5
            goalscoredindex = 6
            goalsconcededindex = 7
            gdindex = 8
            pointsindex = 9

            for i in range(0, len(team)):
                teamlist.append(team[i].get("data-long-name"))
                teamname = teamlist[i]
                
                pos = rest[posindex].text
                played = rest[playedindex].text
                win = rest[winindex].text
                draw = rest[drawindex].text
                lose = rest[lossindex].text
                goalscored = rest[goalscoredindex].text
                goalsconceded = rest[goalsconcededindex].text
                gd = rest[gdindex].text
                points = rest[pointsindex].text
                posindex += jump
                playedindex += jump
                winindex += jump
                drawindex += jump
                lossindex += jump
                goalscoredindex += jump

                goalsconcededindex += jump
                gdindex +=  jump
                pointsindex += jump
                
                # If the list is empty, there is no information on form. 
                # This happens on table for previous years
                try:
                    newform = self.checkForm(form[i], i)
                except IndexError:
                    newform = [0, 0, 0]

                t.add_row([pos, teamname, played, win, draw, lose, goalscored, goalsconceded, gd, points, newform])

            print(t)
            tablenum += 1

        # Print key info like champions league spots, relegation etc...
        for child in key_info.children:
            if child.string != None and child.string != "Key":
                print(child.string)
            if child.string == "Key":
                print("\n")


    # Set the different league based on the input from the user.
    # Do this to make it possible to write the leagues several ways like "pl" or "premier league".
    def determineLeague(self, league):
        premier_league = 'premier league'
        pl = 'pl'
        la_liga = 'la liga'
        bundesliga = 'bundesliga'
        ligue_1 = 'ligue 1'
        championship = 'championship'
        serie_a = 'serie a'
        eredivisie = 'eredivisie'
        cl = 'cl'
        champions_league = 'champions league'
        league_one = 'league one'
        league_two = 'league two'

        if str(league).lower() == premier_league.lower():
            return 'premier-league'
        elif str(league).lower() == pl.lower():
            return 'premier-league'
        elif str(league).lower() == la_liga.lower():
            return 'la-liga'
        elif str(league).lower() == bundesliga.lower():
            return 'bundesliga'
        elif str(league).lower() == ligue_1.lower():
            return 'ligue-1'
        elif str(league).lower() == championship.lower():
            return 'championship'
        elif str(league).lower() == serie_a.lower():
            return 'serie-a'
        elif str(league).lower() == eredivisie.lower():
            return 'eredivisie'
        elif str(league).lower() == cl.lower():
            return 'champions-league'
        elif str(league).lower() == champions_league.lower():
            return 'champions-league'
        elif str(league).lower() == league_one.lower():
            return 'league-1'
        elif str(league).lower() == league_two.lower():
            return 'league-two'

        return league

    # Returns a list of the form for the previous matches [Win, draw, loss]
    def checkForm(self, form, i):
        
        win = 0
        loss = 0
        draw = 0

        for i in range(0, 6):
            if "win" in str(form.findAll('span')[i]):
                win += 1
            if "loss" in str(form.findAll('span')[i]):
                loss += 1
            if "draw" in str(form.findAll('span')[i]):
                draw += 1


        return [win, draw, loss] 


class Scraper:

    def scrapePage(self, url):

        client = requests.get(url)
        page_html = client.text
        client.close
        return page_html

if __name__ == "__main__":
    Main().scrape()
