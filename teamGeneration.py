from player import Player

def listcopy(lista, listb):
    for ele in lista:
        listb.append(ele)

def rest(list):
    return(list[1:len(list)])

def listextend(l, list, a, b):
    list1 = []
    list2 = []
    listcopy(list, list1)
    listcopy(list, list2)

    var0 = []
    var1 = []
    var0.append(0)
    var1.append(1)


    if len(list) == l:
        listofmaps.append(list)
    if a > 0:
        list1.extend(var0)
    if b > 0:
        list2.extend(var1)
    if a > 0:
        listextend(l, list1, (a-1), b)
    if b > 0:
        listextend(l, list2, a, (b-1))


def genmap(length):
    global listofmaps
    print("\ngenerating team maps...\n")
    listofmaps = []
    if length % 2 != 0:
        print("length must be an even number")
    else:
        listextend(length, [], length/2, length/2)
    print("team map generation complete\n")
    return listofmaps[0:int(len(listofmaps)/2)]


def maptoteam(map, pool):
    team1 = []
    team2 = []
    teams = [team1, team2]
    for player in pool:
        if map[0] == 0:
            team1.append(player)
        if map[0] == 1:
            team2.append(player)
        map = rest(map)
    return teams


def getTeamMMR(team):
    sum = 0
    for player in team:
        sum = sum + player.mmr
    return sum / len(team)

def calcBalance(teamlist):
    return abs(getTeamMMR(teamlist[0]) - getTeamMMR(teamlist[1]))
        
def printTeamList(listOfTeams):
    for teamlist in listOfTeams:
        t1mmr = getTeamMMR(teamlist[0])
        t2mmr = getTeamMMR(teamlist[1])
        print("Team 1 MMR avg = {}\t\tTeam 2 MMR avg = {}".format(t1mmr, t2mmr))

def printTeams(teamlist):
    team1 = teamlist[0]
    team2 = teamlist[1]
    print("Team1:\t\t\t\tTeam2:\n")
    for i in range(5):
        print("{}\t{}\t{}\t{}".format(team1[i].member, team1[i].mmr, team2[i].member, team2[i].mmr))

def genteamlist(pool):
    poolsize = len(pool)
    teamlist = []
    maplist = genmap(poolsize)
    for map in maplist:
        teamlist.append(maptoteam(map, pool))
    teamlist.sort(reverse=False, key=calcBalance)
    return teamlist

if __name__ == "__main__":
    player1 = Player(1, 108305168, "Moff", 1234)
    player2 = Player(2, 176488059, "BowiE", 1234)
    player3 = Player(3, 177214200, "Josh", 1234)
    player4 = Player(4, 295355615, "Mumbo", 1234)
    player5 = Player(5, 60623475, "Liver", 1234)
    player6 = Player(6, 121958788, "Ryan", 1234)
    player7 = Player(7, 106614459, "iaa", 1234)
    player8 = Player(8, 141671423, "FooSquash", 1234)
    player9 = Player(9, 108288202, "Fell", 1234)
    player10 = Player(10, 250970093, "Buying Onions", 1234)
    pool = [player1, player2, player3, player4, player5, player6, player7, player8, player9, player10]
    tl = genteamlist(pool)
    printTeamList(tl)
    printTeams(tl[0])
    print(calcBalance(tl[0]))