import cassiopeia as cass
import requests
import numpy as np
import cv2 as cv
import threading
import multiprocessing
from time import time, sleep
from PIL import Image
from mss import mss
import os
from pygame import mixer

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
API_KEY = ''
region = 'EUNE'
cass.set_riot_api_key(API_KEY)
summonername = ''
width = 200 #window_width
height = 600 #window_height
res_w = 1920
res_h = 1080
w_diff = res_w-width
icon_w = 40
icon_h = 40
FileDict = {
  "Turret": "turretdestroyed.mp3",
  "Chemtech": "otherdrakeslain.mp3",
  "Cloud": "otherdrakeslain.mp3",
  "Hextech": "otherdrakeslain.mp3",
  "Infernal": "infernalslain.mp3",
  "Mountain": "otherdrakeslain.mp3",
  "Ocean": "otherdrakeslain.mp3",
  "Baron": "baronslain.mp3",
  "Elder": "elderslain.mp3",
  "Rift": "riftslain.mp3"
}

def GetChampPlayed():
    summoner = cass.get_summoner(name=summonername, region=region)
    try:
        id = summoner.id
    except:
        print(f'Summoner {summonername} does not exist or bad API_KEY')
        exit(1)

    champions = cass.get_champions(region=region)
    API_LINK = f'https://eun1.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{summoner.id}?api_key={API_KEY}'
    response = requests.get(API_LINK)
    if response.status_code == 200:
        injson = response.json()
        for participant in injson['participants']:
            if participant['summonerName'] == summoner.name:
                # print(participant['summonerName'])
                # print(participant['championId'])
                for champ in champions:
                    if champ.id == participant['championId']:
                        return champ.name
    else:
        print(f'Player {summonername} is not in game... trying again')
        exit(1)

def CreateScreenshot():
    mon = {'top' : 0, 'left' : w_diff, 'width' : width, 'height' : height}
    sct = mss()
    sct_img = sct.grab(mon)
    screenshot = Image.frombytes( 'RGB', (sct_img.size.width, sct_img.size.height), sct_img.rgb )
    screenshot = np.array(screenshot)
    screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2RGB)
    screenshot = screenshot[:,:,:3]

    return screenshot

def FindOtherEntity(report,entity,listOfEntities):
    # print(f'process started entity: {entity} {report[2]}')
    threshold = 0.75
    if report[2] == 0:
        screenshot = CreateScreenshot()
        entity_sqr= cv.imread(f"images/entities/{entity}.jpg",cv.IMREAD_UNCHANGED)
        entity_sqr = cv.resize(entity_sqr,(icon_w,icon_h))
        entity_sqr = entity_sqr[:,:,:3]
        result = cv.matchTemplate(screenshot, entity_sqr, cv.TM_CCOEFF_NORMED)

        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        # print(f'max_val match for entity {entity} : {max_val}')


        if max_val >= threshold:
            # print(f'Entity: {entity}')
            report[2] = entity
        else:
            report[0] += 1
            if report[0] >= len(listOfEntities):
                report[2] = 'Player'

def FindOtherEntityHandler(report):
    listOfEntities = ['Turret','Chemtech','Cloud','Hextech','Infernal','Mountain','Ocean','Baron','Elder','Rift']
    # listOfEntities = ['Turret3']
    for entity in listOfEntities:
        p = threading.Thread(target=FindOtherEntity, args=[report,entity,listOfEntities])
        p.start()
    # p.join()

def MultiKillMonitor(multikill):
    while(1):
        if(len(multikill))>0:
            if multikill[0] > 0 and multikill[0] <= 5:
                curr_time = time()
                time_of_kill = multikill[1]
                if curr_time - time_of_kill >= 10:
                    multikill[0] = 0

def KillFeedfunc(killfeed,message_list):
    # print(f'killfeed1 : {killfeed}')
    if len(killfeed)>0:
        if len(killfeed) == 2:
            print('MESSAGE_SUICIDE')
            message_list.append('suicide.mp3')
        else:
            if killfeed[0][2] == 'Player':
                if killfeed[0][1] == 1:
                    multikill[0] += 1
                    multikill[1] = time()

                    if multikill[0] == 1:
                        print('Player Killed')
                        message_list.append('playerkilled.mp3')
                    elif multikill[0] == 2:
                        print('DoubleKill')
                    elif multikill[0] == 3:
                        print('TripleKill')
                        message_list.append('multikill.mp3')
                    elif multikill[0] == 4:
                        print('QuadraKill')
                    elif multikill[0] == 5:
                        print('PentaKill')
                        message_list.append('pentakill.mp3')
                        multikill[0] = 0

                elif killfeed[0][1] == 0:
                    print('Death by player')
                    message_list.append('death.mp3')
            else:
                if killfeed[0][1] == 1:
                    print(f'{report[2]} destroyed')
                    message_list.append(FileDict[report[2]])
                elif killfeed[0][1] == 0:
                    print(f'Killed by {report[2]}')
                    message_list.append('deathbynonplayer.mp3')




        del killfeed[0]
        if len(killfeed)>0:
            del killfeed[0]
        report[2] = 0
        report[0] = 0
        # print(f'killfeed2 : {killfeed}')

def SayMessageInMyStead(message_list):
    cwd = os.getcwd()
    os.chdir(cwd+'/audiomessages')
    mixer.init(devicename='VoiceMeeter Aux Input (VB-Audio VoiceMeeter AUX VAIO)')
    while(1):
        if(len(message_list)>0):
            print(message_list)
            sound = message_list[0]
            mixer.music.load(sound)
            mixer.music.set_volume(1)
            mixer.music.play()
            while mixer.music.get_busy():
                pass
            del message_list[0]


if __name__ == '__main__':
    champ = ''
    while(len(champ) == 0):
        try:
            champ = GetChampPlayed()
        except:
            champ = ''
            sleep(10)

    print(f'champ played: {champ}')

    manager = multiprocessing.Manager()

    # report[0] = counter - if entity was not matched -> counter++
    # report[1] = status - kill(1) or death(0)
    # report[2] = entity - [Turret,...,Player]
    report = [0,0,0]
    multikill = manager.list()
    multikill[:] = [0,0]
    message_list = manager.list()

    handler_called = False
    killfeed = []
    prev_len = 0

    p = multiprocessing.Process(target=MultiKillMonitor, args=[multikill])
    p.start()

    p1 = multiprocessing.Process(target=SayMessageInMyStead, args=[message_list])
    p1.start()

    # loop_time = time()
    while(1):
        screenshot = CreateScreenshot()

        champ_sqr = cv.imread(f"images/{champ}Square.png",cv.IMREAD_UNCHANGED)
        champ_sqr = cv.resize(champ_sqr,(icon_w,icon_h))
        champ_sqr = champ_sqr[:,:,:3]
        result = cv.matchTemplate(screenshot, champ_sqr, cv.TM_CCOEFF_NORMED)


        threshold = 0.85
        locations = np.where(result >= threshold)
        locations = list(zip(*locations[::-1]))

        rectangles = []

        for loc in locations:
            x = int(loc[0])
            y = int(loc[1])
            if ((x in range(1794-w_diff,1794-w_diff+icon_w)) or (x in range(1913-w_diff-icon_w,1913-w_diff))) and (y in range(248,288)):
                rect = [x, y, icon_w, icon_h]
                #append twice so groupRectangles does not remove singles
                rectangles.append(rect)
                rectangles.append(rect)

        #weights is not used, but has to be there because of syntax
        rectangles, weights = cv.groupRectangles(rectangles, 1, 0.8)

        #draws a red rectangle in the place of search
        cv.rectangle(screenshot,(1794-w_diff,248),(1794-w_diff+icon_w,288),color=(0,0,255), thickness=2, lineType=cv.LINE_4)
        cv.rectangle(screenshot,(1912-w_diff-icon_w,248),(1912-w_diff,288),color=(0,0,255), thickness=2, lineType=cv.LINE_4)

        # print(len(rectangles))
        if len(rectangles)<prev_len:
            print(f'Icon disappeared {len(rectangles)}')
            KillFeedfunc(killfeed,message_list)
            #message read, so FindOtherEntityHandler can be called again
            handler_called = False

        if len(rectangles)>0 and handler_called == False:
            print(f'Icon appeared {len(rectangles)}')
            FindOtherEntityHandler(report)
            handler_called = True

        prev_len = len(rectangles)


        if len(rectangles):
            for (x, y, w, h) in rectangles:
                top_left = (x, y)
                top_right_x = (x + w)
                bottom_right = (x + w, y + h)
                cv.rectangle(screenshot,top_left,bottom_right,color=(0,255,0), thickness=2, lineType=cv.LINE_4)
                diff = screenshot.shape[1] - top_right_x

                if diff >= 86:
                    report[1] = 1
                else:
                    report[1] = 0
                # print(report)

                if [0,report[1],report[2]] not in killfeed and report[2] != 0:
                    killfeed.append([0,report[1],report[2]])
                    # print(f'report: {list(report)}')



        #cv.imshow('Title',screenshot)
        # print(f'{1/(time()-loop_time)} FPS')
        # loop_time = time()
        if cv.waitKey(1) == ord('x'):
            cv.destroyAllWindows()
            p.join()
            break
