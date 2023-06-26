import psycopg2
from data import credentials
from flask import session
def matchSetup(players):
    session['scores'] = []
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    Query = """INSERT INTO "Matches"(place) VALUES('REMOVE') RETURNING match_id;"""
    cursor.execute(Query)
    matchID = (cursor.fetchall())[0][0]
    conn.commit()
    gameID = gameSetup(matchID)
    insertPlayers(players,matchID)
    return matchID, gameID

def gameSetup(matchID):
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    Query = """INSERT INTO "Games"(match_id) VALUES (%s) RETURNING game_id;"""
    cursor.execute(Query, (matchID,))
    gameID = (cursor.fetchall())[0][0]
    conn.commit()
    return gameID


def insertPlayers(players, matchID):
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    Query = """INSERT INTO "PlayerInGame"(match_id, player_id, home_away) VALUES(%s,%s,%s)"""
    for x in range (0,2):
        cursor.execute(Query,(matchID,players[x],x))
    conn.commit()
    return
def insertRound(gameID,roundID,scores, closerPoints):
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    Query = """INSERT INTO "Rounds"(game_id, round_id, home_score, away_score, home_closer, away_closer) VALUES (%s,%s,%s,%s,%s,%s)"""
    data = (gameID, roundID, scores[0],scores[1],closerPoints[0],closerPoints[1])
    cursor.execute(Query, data)
    conn.commit()
    return