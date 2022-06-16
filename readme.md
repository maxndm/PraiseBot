
# League of Legends PraiseBot

Bot which praises my duo friend for killing enemy champions, monsters and objectives.
Platform: Windows

## How does it work?

Program gets player's champion name from current game using League of legends API (API_KEY is needed), so it can choose which champion square picture is monitored and then proceeds to capture the screen (part of the screen where killfeed is for better performance). When champion square picture is detected, multiple threads are spawned to check which entity, apart monitored player, is on the screen so message can be generated. When champion square disappears, message is appended into message_list and parallel process plays voice message from that list based on entity and kill status (death or kill).

The voice message is mixed with microphone input using VoiceMeeter banana, so I can talk when I need to and let my duo be praised by bot instead of me.

## images

Champion square pictures can be downloaded using script "download_pictures.py" in "images" folder


## Libraries

```sh
pip install cassiopeia
pip install opencv-python
pip install pyautogui
pip install pywin32
pip install image
pip install mss
pip install pygame
```

## Goodies
OpenCV basics<br>
  https://www.youtube.com/watch?v=m1pbF9BW8tA&list=PL1m2M8LQlzfKtkKq2lK5xko4X-8EZzFPI&index=3<br>
Voicemeeter<br>
  https://vb-audio.com/Voicemeeter/banana.htm
