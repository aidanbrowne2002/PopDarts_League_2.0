import data.update
import psycopg2
from flask import session
from data import update, add, get
# CompVision Stuff
import cv2, os
#from compVision import helper as hp, warp_img as wImg, round_score as rs, score_class as score

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
def camera_on():
    camera_found = False
    global camera
    for camera_index in range(10):  # Try camera indexes 0 to 9
        camera = cv2.VideoCapture(camera_index)
        if camera.isOpened():
            print('on',camera_index)
            camera_found = True
            break

    if not camera_found:
        print("set 0 - No camera found.")

def camera_off():
    if 'camera' in globals():
        camera.release()
    else:
        print('No camera on atm')

def generate_frames(capture):
    while True:
        success, frame = camera.read()
        if not success:
            break
        if capture:
            print("PICTURE TAKEN")
            capture=0
            p = os.path.sep.join(['compVision/rounds', f"rounds_{get_next_round_number()}.jpg"])
            cv2.imwrite(p, frame)
        try:
            ret, buffer = cv2.imencode('.jpg',frame)
            frame = buffer.tobytes()
            yield(b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n') # generates the next frame
        except Exception as e:
            pass

def logic(r_image):
    # wImg.unwarp_img('compVision/round_image') # Toggle
    labels, boxes, scores = hp.load_model(r_image) # Will need to find a way to get latest image
    center_darts, labels, boxes, scores = hp.clean_data(labels, boxes, scores)
    # print(boxes)
    # print(center_darts)
    closest, team, closest_points = rs.dart_system(labels, center_darts)
    return team, closest, closest_points

def last_image():
    files = os.listdir('compVision/rounds')
    image_files = [file for file in files if file.startswith('rounds_') and file.endswith('.jpg')]
    sorted_files = sorted(image_files)
    if sorted_files:
        last_image = sorted_files[-1]
        return last_image
    else:
        print("No image")

def get_next_round_number():
    saved_files, temp_files = os.listdir('compVision/all_rounds'), os.listdir('compVision/rounds')
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

'''def convertimage(data):
    import pybase64
    data += "=" * ((4 - len(data) % 4) % 4)  # ugh
    with open("footon.png", "wb") as f:
        f.write(pybase64.b64decode(data))
convertimage('iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAApgAAAKYB3X3/OAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAANCSURBVEiJtZZPbBtFFMZ/M7ubXdtdb1xSFyeilBapySVU8h8OoFaooFSqiihIVIpQBKci6KEg9Q6H9kovIHoCIVQJJCKE1ENFjnAgcaSGC6rEnxBwA04Tx43t2FnvDAfjkNibxgHxnWb2e/u992bee7tCa00YFsffekFY+nUzFtjW0LrvjRXrCDIAaPLlW0nHL0SsZtVoaF98mLrx3pdhOqLtYPHChahZcYYO7KvPFxvRl5XPp1sN3adWiD1ZAqD6XYK1b/dvE5IWryTt2udLFedwc1+9kLp+vbbpoDh+6TklxBeAi9TL0taeWpdmZzQDry0AcO+jQ12RyohqqoYoo8RDwJrU+qXkjWtfi8Xxt58BdQuwQs9qC/afLwCw8tnQbqYAPsgxE1S6F3EAIXux2oQFKm0ihMsOF71dHYx+f3NND68ghCu1YIoePPQN1pGRABkJ6Bus96CutRZMydTl+TvuiRW1m3n0eDl0vRPcEysqdXn+jsQPsrHMquGeXEaY4Yk4wxWcY5V/9scqOMOVUFthatyTy8QyqwZ+kDURKoMWxNKr2EeqVKcTNOajqKoBgOE28U4tdQl5p5bwCw7BWquaZSzAPlwjlithJtp3pTImSqQRrb2Z8PHGigD4RZuNX6JYj6wj7O4TFLbCO/Mn/m8R+h6rYSUb3ekokRY6f/YukArN979jcW+V/S8g0eT/N3VN3kTqWbQ428m9/8k0P/1aIhF36PccEl6EhOcAUCrXKZXXWS3XKd2vc/TRBG9O5ELC17MmWubD2nKhUKZa26Ba2+D3P+4/MNCFwg59oWVeYhkzgN/JDR8deKBoD7Y+ljEjGZ0sosXVTvbc6RHirr2reNy1OXd6pJsQ+gqjk8VWFYmHrwBzW/n+uMPFiRwHB2I7ih8ciHFxIkd/3Omk5tCDV1t+2nNu5sxxpDFNx+huNhVT3/zMDz8usXC3ddaHBj1GHj/As08fwTS7Kt1HBTmyN29vdwAw+/wbwLVOJ3uAD1wi/dUH7Qei66PfyuRj4Ik9is+hglfbkbfR3cnZm7chlUWLdwmprtCohX4HUtlOcQjLYCu+fzGJH2QRKvP3UNz8bWk1qMxjGTOMThZ3kvgLI5AzFfo379UAAAAASUVORK5CYII=')
'''