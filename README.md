## Mycroft Youtube Mpv
Searches and plays youtube videos with help of mpv media player

## Description 
Youtube Mpv is a powerful tool on base of the mpv player that uses the mpv unix
socket to play and control youtube videos only with help of voice commands.<br>
It also checks if mpv is running to avoid not wanted simultaneous mpv sessions.

## Examples 
* "Youtube arianna grande 7 rings" -- plays first result
* "Youtube cancel|exit" -- stops playing
* "Youtube pause|wait" -- pause playing
* "Youtube resume|play" -- resume playing
* "Youtube volume up|down|20" -- set volume up, down, to number from 0 - 100
* "Youtube speed up|down|2" -- set spee up, down, to floating point number from 0 - 5
* "Youtube get duration" -- get video duration
* "Youtube get remaining" -- get remaining video time 
* "Youtube get position" -- get current time stamp
* "Youtube get volume" -- get current volume
* "Youtube get speed" -- get current speed
* "Youtube seek forward|backward|num" -- seek for/backward or with integer num (+/-)

## Requiements
Programs:
* mpv 
* youtube-dl

Python-libs:
* bs4

## Supported plattforms
* Linux Desktop (KDE)

## TODO
* Playing more than first search result
* Playing yt playlists
* Config file with default values
* No-GUI mode for Raspian
* German translation

## Credits 
Philip Mayer

## License 
MIT
