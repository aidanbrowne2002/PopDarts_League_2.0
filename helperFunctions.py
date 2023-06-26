import data.update
import psycopg2
from flask import session
from data import update, add, get

def newGame(matchID, gameID, winner):
    newGameID = data.add.gameSetup(matchID)
    session['gameID'] = newGameID
    session['scores'] = []
    return

def checkWinner(matchID):
    print("here is matchid   ", matchID)
    result = get.result(matchID)
    print ("result", result)
    if result[0]>=3 or result[1]>=3:
        print ("3-0 happened")
        print (result[0])
        print (result[1])
        if result[0] > result[1]:
            winner = 0
        else:
            winner = 1
        print (winner)
        return winner
    else:
        return "no"

def finishMatch(matchID, result, players, p1score, p2score):
    print ("scores at end are", p1score, p2score)
    scores = (p1score, p2score)
    data.update.match(matchID,result)
    playersRRchange = changerr(players[0],p1score,data.get.rating(players[0]),players[1],p2score,data.get.rating(players[1]))
    for x in range (0,2):
        data.update.playerInGame(matchID,players[x], playersRRchange[x],scores[x])
        data.update.changeRR(players[x],data.get.gameRRChange(players[x],matchID))


def changerr(player1, p1score, rating1, player2, p2score, rating2):

    # Determine who won and the score difference
    if p1score > p2score:
        winner = 1
        score_diff = p1score - p2score
    elif p2score > p1score:
        winner = 2
        score_diff = p2score - p1score
    else:
        # If it's a draw, return 0 changes
        return (0, 0)

    # Base change in rating, proportional to score difference with a minimum of 10
    base_change = max(score_diff * 10, 10)

    # Calculate bonus based on rating difference
    if winner == 1:
        bonus = max((rating2 - rating1) / 10, 0)
        changeinrank1 = base_change + bonus
        changeinrank2 = -base_change - bonus
    else:
        bonus = max((rating1 - rating2) / 10, 0)
        changeinrank1 = -base_change - bonus
        changeinrank2 = base_change + bonus

    return (changeinrank1, changeinrank2)

