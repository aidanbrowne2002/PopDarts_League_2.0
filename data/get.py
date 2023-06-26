from data import credentials
import psycopg2
from flask import session

def f_names():                                                  #Get first name of all users
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    Query = """SELECT f_name FROM "Users";"""
    cursor.execute(Query)
    data = (cursor.fetchall())
    result = []
    for x in range (0,len(data)):
        result.append(data[x][0])
    return result

def usernames(): #Currently f_names
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    Query = """SELECT username FROM "Users";"""
    cursor.execute(Query)
    data = (cursor.fetchall())
    result = []
    for x in range (0,len(data)):
        result.append(data[x][0])
    result = [name for name in result if name is not None]
    return result

def getIdFromUsername(name): #currently f_name
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    Query = """SELECT id FROM "Users" where username = %s"""
    cursor.execute(Query, (name,))
    return (cursor.fetchone()[0])
def getNextRound(matchID, gameID):
    print(matchID, gameID)
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    Query = """SELECT round_id FROM "Rounds"
                JOIN "Games" G on G.game_id = "Rounds".game_id WHERE match_id = %s and G.game_id = %s
                ORDER BY round_id;"""
    data = (matchID, gameID)
    cursor.execute(Query, data)
    try:
        result = cursor.fetchone()[0]
    except:
        result = 0
    print (result)
    if result:
        round = result
    else:
        round = 0
    return round+1

def RRChange(user):
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    Query = """SELECT "PlayerInGame".rr_change, "Matches".match_id FROM "PlayerInGame"
            inner join "Users" on "Users".id = "PlayerInGame".player_id
            inner join "Matches" on "Matches".match_id = "PlayerInGame".match_id
            where "Users".id = %s;"""
    cursor.execute(Query, (user,))
    data = cursor.fetchall()
    x=[0]
    y=[0]
    for i in range (0, len(data)):
        x.append(data[i][1])
        y.append(y[i]+data[i][0])
    data = (x,y)
    return data



def result(matchID):
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    Query = """SELECT winner from "Games" where match_id = %s"""
    cursor.execute(Query, (matchID,))
    data = cursor.fetchall()
    actualdata = []
    for i in range(0,len(data)):
        actualdata.append(data[i][0])
    player1 = actualdata.count(0)
    player2 = actualdata.count(1)
    return player1, player2

def rating(user_id):
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    Query = """SELECT rating FROM "Users" WHERE id = %s;"""
    cursor.execute(Query,(user_id,))
    return cursor.fetchone()[0]

def gameRRChange(userID, matchID):
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    Query = """SELECT rr_change from "PlayerInGame" where match_id = %s and player_id = %s"""
    data = (matchID, userID)
    cursor.execute(Query, data)
    result = int(cursor.fetchone()[0])
    return result

def matchAverages(matchID):
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    Query = """SELECT ROUND(avg(home_score),2), ROUND(avg(away_score),2) FROM "Rounds" JOIN "Games" G on G.game_id = "Rounds".game_id JOIN "Matches" M on G.match_id = M.match_id
                WHERE G.match_id = %s;"""
    cursor.execute(Query, (matchID,))
    result = cursor.fetchall()[0]
    print(result)
    return result
def gameAverages(matchID, gameID):
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    Query = """SELECT ROUND(avg(home_score),2), ROUND(avg(away_score),2) FROM "Rounds" JOIN "Games" G on G.game_id = "Rounds".game_id JOIN "Matches" M on G.match_id = M.match_id
                WHERE G.match_id = %s and G.game_id = %s;"""
    cursor.execute(Query, (matchID, gameID))
    result = cursor.fetchall()[0]
    print (result)
    return result

def roundData(matchID):
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    Query = """SELECT home_score, away_score, row_number() over () AS ID from "Rounds" join "Games" G on G.game_id = "Rounds".game_id join "Matches" M on M.match_id = G.match_id where M.match_id = %s;"""
    cursor.execute(Query, (matchID,))
    result = cursor.fetchall()
    print(result)
    return result

def closer(matchID):
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    Query = """SELECT sum(home_closer), sum(away_closer) from "Rounds" join "Games" G on G.game_id = "Rounds".game_id join "Matches" M on M.match_id = G.match_id where M.match_id = %s;"""
    cursor.execute(Query, (matchID,))
    result = cursor.fetchall()[0]
    print(result)
    return result

def countBetterRounds():
    p1 =0
    p2 =0
    draw =0
    print (session['scores'])
    for x in range (0, len(session['scores'])):
        if session['scores'][x][1] > session['scores'][x][3]:
            p1 += 1
        if session['scores'][x][1] < session['scores'][x][3]:
            p2 += 1
        else:
            draw +=1
    print(p1,p2,draw)
    return p1, p2, draw


def IDs():
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    Query = """SELECT id FROM "Users";"""
    cursor.execute(Query)
    data = (cursor.fetchall())
    result = []
    for x in range(0, len(data)):
        result.append(data[x][0])
    return result

def name(id): #currently f_name
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    Query = """SELECT f_name FROM "Users" where id = %s"""
    cursor.execute(Query, (id,))
    return (cursor.fetchone()[0])
def graphdata():
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    user_ids = IDs()  # Example user ids

    all_players_data = {}
    for user_id in user_ids:
        Query = """SELECT "Matches".match_id, SUM("PlayerInGame".rr_change) as change FROM "PlayerInGame"
                INNER JOIN
                    "Users" ON "PlayerInGame".player_id = "Users".id
                INNER JOIN
                    "Matches" ON "Matches".match_id = "PlayerInGame".match_id
                WHERE player_id = %s and "Matches".complete = True
                GROUP BY "Matches".match_id
                order by match_id"""
        cursor.execute(Query, (user_id,))
        data = cursor.fetchall()
        data = [list(item) for item in data]  # Convert tuples to lists
        for x in range(1, len(data)):
            data[x][1] = data[x][1] + data[x - 1][1]

        player_name = name(user_id)  # Use your function to get the user's name
        all_players_data[player_name] = data  # Store each player's data using their name as the key

    return all_players_data