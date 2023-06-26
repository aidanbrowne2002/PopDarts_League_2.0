import data.credentials
import helperFunctions
from flask import Flask, render_template, session, request, redirect
import data.get
import data.add
import data.remove
import data.update
from datetime import datetime
import psycopg2

app = Flask(__name__)
app.secret_key = data.credentials.secretkey


@app.route('/')
def home():  # put application's code here
    return render_template('index.html', graph = data.get.graphdata())


import psycopg2
from psycopg2 import sql

# ...

@app.route('/notifications')
def notifications():
    conn = psycopg2.connect(
        host=data.credentials.host,
        port=data.credentials.port,
        dbname=data.credentials.database,
        user=data.credentials.user,
        password=data.credentials.password
    )
    cursor = conn.cursor()

    # Retrieve notifications from the database
    query = sql.SQL("SELECT * FROM {}").format(sql.Identifier("Notifications"))
    cursor.execute(query)
    notification_data = cursor.fetchall()

    notifications = [
        {
            'id': data[0],
            'title': data[1],
            'content': data[2],
            'link_text': data[3],
            'link': data[4],
            'timestamp': data[5]
        }
        for data in notification_data
        if data[0] not in session.get('dismissed_notifications', [])
    ]

    cursor.close()
    conn.close()

    return render_template('notifications.html', notifications=notifications)

@app.route('/dismiss_notification/<int:notification_id>')
def dismiss_notification(notification_id):
    # Initialize the 'dismissed_notifications' list in the session if it doesn't exist
    if 'dismissed_notifications' not in session:
        session['dismissed_notifications'] = []
    # Add the dismissed notification ID to the session
    session['dismissed_notifications'].append(notification_id)
    session.modified = True  # This is necessary because we're modifying a mutable type (list)
    return '', 204  # Return an empty response with status code 204 (No Content)


@app.route('/gamesetup', methods=['GET', 'POST'])
def gamesetup():
    autocomplete = data.get.usernames()
    if request.method == 'POST':
        session['player1'] = request.form.get('player1')
        session['player2'] = request.form.get('player2')
        players = [data.get.getIdFromUsername(session['player1']), data.get.getIdFromUsername(session['player2'])]
        returned = data.add.matchSetup(players)
        session['matchID'] = returned[0]
        session['gameID'] = returned[1]
        return redirect('/manualscore')
    return render_template('gamesetup.html', autocompleteData=autocomplete)






gscore = []

@app.route('/manualscore', methods=['GET', 'POST'])
def manualscore():                                                                     #Must have MatchID and GameID
    if not session['gameID'] and not session['matchID']:
        return redirect('/gamesetup')
    session['round'] = data.get.getNextRound(session['matchID'], session['gameID'])
    player1 = session['player1']
    player2 = session['player2']
    tscore1 = 0
    tscore2 = 0
    winner = None
    if request.method == 'POST':
        score1 = request.form.get('score1')
        score2 = request.form.get('score2')
        closer = request.form.get('who')
        numCloser = request.form.get('closer')
        if closer == "0":
            closerPoints = (numCloser, 0)
        elif closer == "1":
            closerPoints = (0, numCloser)
        else:
            closerPoints = (0,0)
        print ("closer points:",closerPoints)
        if score1 != None:
            session['scores'].append([player1,score1,player2,score2])
            data.add.insertRound(session['gameID'],session['round'],(score1,score2), closerPoints)
        print(session['scores'])
    for round in range(0,len(session['scores'])):
        tscore1 = tscore1 + int(session['scores'][round][1])
        tscore2 = tscore2 + int(session['scores'][round][3])
    if (tscore1 >= 11 or tscore2 >= 11) and (tscore1 != tscore2):
        if tscore1 > tscore2:
            result = 0
            winner = player1
        else:
            result = 1
            winner = player2
        data.update.gameWinner(session['matchID'], session['gameID'], result)
        if (helperFunctions.checkWinner(session['matchID']) == "no"):
            print("game not won")
            helperFunctions.newGame(session['matchID'], session['gameID'], result)
        else:
            helperFunctions.finishMatch(session['matchID'], result, (data.get.getIdFromUsername(player1), data.get.getIdFromUsername(player2)),data.get.result(session['matchID'])[0],data.get.result(session['matchID'])[1])
            print("game has been won")
            return redirect('/gamefinish')
        tscore1 = 0
        tscore2 = 0
    gscores = data.get.result(session['matchID'])
    gdata = data.get.roundData(session['matchID'])
    home_scores = [score[0] for score in gdata]
    away_scores = [score[1] for score in gdata]
    rounds = [score[2] for score in gdata]
    data.get.countBetterRounds()
    return render_template('manualscore.html', scores=session['scores'], player1=player1, player2=player2, matchid = session['matchID'], gameid = session['gameID'], tscore1=tscore1, tscore2=tscore2, gscores = gscores, matchAverages = data.get.matchAverages(session['matchID']), gameAverages = data.get.gameAverages(session['matchID'],session['gameID']), home_scores=home_scores, away_scores=away_scores, rounds=rounds, pie = data.get.closer(session['matchID']), betterRound = data.get.countBetterRounds())

@app.route('/undo', methods=['POST'])
def undo():
    if session['scores']:
        session['scores'].pop()
        session.modified = True
        data.remove.undoRound(session['gameID'], session['round'])
    return redirect('/manualscore')

@app.route('/gamefinish')
def gamefinish():
    result = data.get.result(session['matchID'])
    rrchange1 = data.get.gameRRChange(data.get.getIdFromUsername(session['player1']), session['matchID'])
    rrchange2 = data.get.gameRRChange(data.get.getIdFromUsername(session['player2']), session['matchID'])
    return render_template('gameEnd.html', result = result,rrchange1=rrchange1,rrchange2=rrchange2)


@app.route('/graph')
def graph():
    gdata = data.get.roundData(session['matchID'])
    home_scores = [score[0] for score in gdata]
    away_scores = [score[1] for score in gdata]
    rounds = [score[2] for score in gdata]
    return render_template('testgraphs.html', home_scores=home_scores, away_scores=away_scores, rounds=rounds)

if __name__ == '__main__':
    app.run()