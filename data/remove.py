from data import credentials
import psycopg2

def undoRound(gameID, roundID):
    print(roundID)
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    Query = """DELETE FROM "Rounds" WHERE round_id = %s AND game_id = %s;"""
    data = (roundID, gameID)
    cursor.execute(Query, data)
    conn.commit()
    return