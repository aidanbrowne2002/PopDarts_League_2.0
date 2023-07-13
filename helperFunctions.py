import data.update
import psycopg2
from flask import session
from data import update, add, get
# CompVision Stuff
import cv2, os
from compVision import helper as hp, warp_img as wImg, round_score as rs, score_class as score

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

# Computer Vision Score tracker
def create_class():
    global scores
    scores = score.Scores()

def update_scores(b,g):
    print(b,g)
    scores.update_scores(b, g)

def get_team(colour):
    if colour == 'blue':
        return scores.get_blue()
    elif colour == 'green':
        return scores.get_green()
    else:
        print('incorrect team')

def get_round(colour):
    if colour == 'blue':
        return scores.get_rounds_blue()
    elif colour == 'green':
        return scores.get_rounds_green()
    else:
        print('incorrect team')

def check_score(matchID, gameID):
    print(matchID, gameID)
    gameResult = None
    if scores.get_blue() >= 11 and scores.get_blue() > scores.get_green(): # game won b
        data.update.gameWinner(matchID, gameID, 0)
        scores.update_rounds('blue')
        scores.reset_scores()
        gameResult = 0
    elif scores.get_green() >= 11 and scores.get_green() > scores.get_blue(): # game won g
        data.update.gameWinner(matchID, gameID, 1)
        scores.update_rounds('green')
        scores.reset_scores()
        gameResult = 1

    if scores.get_rounds_blue() == 3:
        # scores.reset_rounds()
        return 'match won blue', gameResult
    elif scores.get_rounds_green() == 3:
        # scores.reset_rounds()
        return 'match won green', gameResult
    return None, gameResult

# Computer Vision
def logic(r_image):
    # wImg.unwarp_img('compVision/round_image') # Toggle
    labels, boxes, scores = hp.load_model(r_image) # Will need to find a way to get latest image
    center_darts, labels, boxes, scores = hp.clean_data(labels, boxes, scores)
    # print(boxes)
    # print(center_darts)
    closest, team, closest_points = rs.dart_system(labels, center_darts)
    return team, closest, closest_points

def last_image():
    files = os.listdir('compVision/all_rounds')
    image_files = [file for file in files if file.startswith('image_') and file.endswith('.jpg')]
    sorted_files = sorted(image_files)
    if sorted_files:
        last_image = sorted_files[-1]
        return last_image
    else:
        print("No image")

def get_next_round_number():
    saved_files, temp_files = os.listdir('compVision/all_rounds'), os.listdir('compVision/all_rounds')
    if saved_files:
        round_numbers = get_files(saved_files)
    else:
        round_numbers = get_files(temp_files)
    if round_numbers:
        return max(round_numbers) + 1
    return 1

def get_files(dir):
    round_numbers = []
    for file in dir:
        round_number = int(file.split('_')[1].split('.')[0])
        round_numbers.append(round_number)
    return round_numbers