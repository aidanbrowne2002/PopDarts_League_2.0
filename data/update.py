import psycopg2
from data import credentials
from data import get
from flask import session

def gameWinner(matchID, gameID, winner):
    print("its happening")
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    Query = """UPDATE "Games" SET winner = %s WHERE match_id = %s AND game_id = %s;"""
    data = (winner, matchID, gameID)
    cursor.execute(Query, data)
    conn.commit()
    return

def playerInGame(matchID, playerID, rrchange, score):
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    Query = """UPDATE "PlayerInGame" SET rr_change = '%s', score = '%s' WHERE match_id = '%s' AND player_id = '%s'"""
    print ("Updating rr")
    data = (rrchange,score, matchID, playerID)
    cursor.execute(Query, data)
    conn.commit()
    return





def match(matchID, result):
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    Query = """UPDATE  "Matches" SET result = %s, complete = TRUE WHERE match_id = %s;"""
    data = (result, matchID)
    cursor.execute(Query, data)
    conn.commit()
    return

def changeRR(userID, rrchange):
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    Query = """UPDATE "Users" set rating = rating + %s where id = %s;"""
    data = (rrchange , userID)
    cursor.execute(Query, data)
    conn.commit()
    return
