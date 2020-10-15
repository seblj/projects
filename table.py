#!//Library/Frameworks/Python.framework/Versions/3.8/bin/python3
# -*- coding: utf-8 -
from bs4 import BeautifulSoup as soup
import requests
from prettytable import PrettyTable
import sys

class Main:
    def __init__(self):
        self.url = "https://www.skysports.com/"
        self.league = ""    
        self.leaguetitle = ""
        self.year = ""

    # Find the year the user wants to see the table for
    def parseArgument(self):

        # if user specifies year, check if writte for example '15' or '2015'
        if len(sys.argv) > 1:
            self.year = sys.argv
            inputyear = self.year.pop(1)
            if len(inputyear) > 2:
                self.year = inputyear
            else:
                self.year = '20' + inputyear[0] + inputyear[1]
 
    # Scrape the page and print football table
    def scrape(self):

        self.parseArgument()

        league = input("Hvilken liga vil du se tabell for?\n")
        self.league = self.determineLeague(league)
        self.url = self.url + self.league + "-table/" + self.year

        page_html = Scraper().scrapePage(self.url)
        page_soup = soup(page_html, "html.parser")
        
        tables = page_soup.findAll("table", {"class":{"standing-table__table"}})
        key_info = page_soup.find("div", {"class":"standing-table__supplementary"})

        if not tables:
            print("Table not found")
            return

        tabledirectory = {}

        for idx, table in enumerate(tables):

            tabledirectory["t{0}".format(idx)]=PrettyTable()
            t = tabledirectory["t" + str(idx)]

            t.field_names = ['#', 'Team', 'P', 'W', 'D', 'L', 'F', 'A', 'GD', 'Pts', 'Form[W,D,L]']
            tabletitle = table.findAll("caption", {"class":"standing-table__caption"})
            t.title = tabletitle[0].text.strip()
            team = table.findAll("td", {"class":"standing-table__cell standing-table__cell--name"})
            rest = table.findAll("td", {"class":"standing-table__cell"})
            form = table.findAll("div", {"class":"standing-table__form"})

            for i in range(0, len(team)):
                
                teamname = team[i].get("data-long-name")
                # calculate position, number of played games, number of wins etc... for each team
                # Some magic numbers for parsing the html
                # 11 is how much to move the index to get to the next team.
                pos = rest[0 + (i * 11)].text
                played = rest[2 + (i * 11)].text
                win = rest[3 + (i * 11)].text
                draw = rest[4 + (i * 11)].text
                lose = rest[5 + (i * 11)].text
                goalscored = rest[6 + (i * 11)].text
                goalsconceded = rest[7 + (i * 11)].text
                gd = rest[8 + (i * 11)].text
                points = rest[9 + (i * 11)].text

                # If the list is empty, there is no information on form. 
                # This happens on table for previous years
                try:
                    newform = self.checkForm(form[i], i)
                except IndexError:
                    newform = [0, 0, 0]

                t.add_row([pos, teamname, played, win, draw, lose, goalscored, goalsconceded, gd, points, newform])

            print(t)

        self.printKeyInfo(key_info)

    # Set the different league based on the input from the user.
    # Do this to make it possible to write the leagues several ways like "pl" or "premier league".
    def determineLeague(self, league):

        league = str(league).lower()

        leaguedict = {
            'premier league' : 'premier-league',
            'pl' : 'premier-league',
            'england' : 'premier-league',
            'la liga' : 'la-liga',
            'spain' : 'la-liga',
            'spania' : 'la-liga',
            'cl' : 'champions-league',
            'champions league' : 'champions-league',
            'serie a' : 'serie-a',
            'italy' : 'serie-a',
            'italia' : 'serie-a',
            'ligue 1' : 'ligue-1',
            'france' : 'ligue-1',
            'frankrike' : 'ligue-1',
            'league one' : 'league-1',
            'leauge 1' : 'league-1',
            'leauge two' : 'league-2',
            'league 2' : 'league-2',
            'nations league' : 'uefa-nations-league',
            'uefa nations league' : 'uefa-nations-league',
            'europa league' : 'europa-league',
            'el' : 'europa-leauge',
            'copa america' : 'copa-america',
            'scottish premiership' : 'scottish-premier-league',
            'scotland' : 'scottish-premier-league'
        }

        try:
            return leaguedict[league]
        except KeyError:
            return league


    # Print important info about the league
    def printKeyInfo(self, key_info):
        for child in key_info.children:
            if child.string != None and child.string != "Key":
                print(child.string)
            if child.string == "Key":
                print("\n")


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
