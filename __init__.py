# MIT LICENSE
# Mycroft Skill: Application Launcher, opens/closes Linux desktop applications
# Copyright © 2019 Philip Mayer philip.mayer@shadowsith.de

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
# OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import subprocess
import json
import urllib.request
from bs4 import BeautifulSoup
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.util.log import LOG

# Each skill is contained within its own class, which inherits base methods
# from the MycroftSkill class.  You extend this class as shown below.
# TODO: Change "Template" to a unique name for your skill


class YoutubeMpvSkill(MycroftSkill):
    def __init__(self):
        super(YoutubeMpvSkill, self).__init__(name="YoutubeMpvSkill")

        self.search = ""
        self.url = ""
        self.volume = 80
        self.mpv_start = "mpv --volume={}\
            --input-ipc-server=/tmp/mpvsocket {} &"
        self.pause_state = "true"

        # if you want add more options use the mpv manpages
        self.mpv_echo = "echo '{}' | socat - /tmp/mpvsocket"

        # setter for unix socket
        self.mpv_pause = '"command": ["set_property", "pause", {}]'
        self.mpv_volume = '"command": ["set_property", "volume", {}]'
        self.mpv_speed = '"command": ["set_property", "speed", {}]'
        self.mpv_seek = '"command": [ "seek", "{}" ]'

        # getter from unix socket
        self.mpv_duration = '"command": ["get_property", "duration"]'
        self.mpv_time_pos = '"command": ["get_property", "time-pos"]'
        self.mpv_time_remaining = '"command": ["get_property", \
            "time-remaining"]'

        self.mpv_stop = "killall mpv"

    def getResults(self, search, pos=0):
        query = urllib.parse.quote(search)
        link = "https://www.youtube.com/results?search_query=" + query
        response = urllib.request.urlopen(link)
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        vids = soup.findAll(attrs={'class': 'yt-uix-tile-link'})
        url = 'https://www.youtube.com' + vids[pos]['href']
        return url

    def mpvExists(self):
        cmd = subprocess.Popen("command -v mpv",
                               stdout=subprocess.PIPE,
                               shell=True).stdout.read()
        cmd = cmd.decode("utf-8")
        if(cmd != ''):
            return True
        else:
            return False

    def mpvStart(self):
        subprocess.call(self.mpv_start
                        .format(self.volume, self.url), shell=True)
        self.speak_dialog("ytmpv.start", data={"search": self.search})
        self.pause_state = "true"

    def mpvPause(self, state):
        self.pause_state = state
        pause = self.mpv_pause.format(self.pause_state)
        cmd = self.mpv_echo.format("{" + pause + "}")
        subprocess.call(cmd, shell=True)

    def mpvStop(self):
        subprocess.call("killall mpv", shell=True)
        self.speak_dialog("ytmpv.stop",
                          data={"search": self.search})
        self.pause_state = "true"

    def mpvChangeVol(self, volume):
        if(volume <= 0):
            volume = 0
        elif(volume >= 100):
            volume = 100

        self.volume = volume
        cmd = self.mpv_echo.format("{" + self.mpv_volume.format(volume) + "}")
        subprocess.call(cmd, shell=True)

    # def mpvSeek(self, secs):

    # def mpvSpeed(self, secs):

    def getDuration(self):
        cmd = self.mpv_echo.format("{" + self.mpv_duration + "}")
        data = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                shell=True).stdout.read()
        j = json.loads(data)
        self.speak_dialog(str(j["data"]))

    def getPosition(self):
        cmd = self.mpv_echo.format("{" + self.mpv_time_pos + "}")
        data = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                shell=True).stdout.read()
        return data["data"]

    def getRemaining(self):
        cmd = self.mpv_echo.format("{" + self.mpv_time_remaining + "}")
        data = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                shell=True).stdout.read()
        return data["data"]

    @intent_handler(IntentBuilder("").require("YoutubeMpv"))
    def handle_youtubempv_intent(self, message):
        try:
            cmd = str(message.data.get('YoutubeMpv'))
            msg = str(message.data.get('utterance')).replace(cmd+" ", "", 1)
            if(self.mpvExists()):
                # TODO adding translations in voc
                self.search = msg
                self.url = self.getResults(self.search)
                self.mpvStart()
            else:
                self.speak_dialog("ytmpv.not.exists")
        except Exception as e:
            LOG.exception("YoutubeMpv Error: " + e.message)
            self.speak_dialog("ytmpv.error")

    @intent_handler(IntentBuilder("").require("YoutubeMpvPause"))
    def handle_youtubempv_pause_intent(self, message):
        try:
            if(self.mpvExists()):
                self.mpvPause("true")
        except Exception as e:
            LOG.exception("YoutubeMpv Error: " + e.message)
            self.speak_dialog("ytmpv.error")

    @intent_handler(IntentBuilder("").require("YoutubeMpvPlay"))
    def handle_youtubempv_play_intent(self, message):
        try:
            if(self.mpvExists()):
                self.mpvPause("false")
            else:
                self.speak_dialog("ytmpv.not.exists")
        except Exception as e:
            LOG.exception("YoutubeMpv Error: " + e.message)
            self.speak_dialog("ytmpv.error")

    @intent_handler(IntentBuilder("").require("YoutubeMpvExit"))
    def handle_youtubempv_exit_intent(self, message):
        try:
            if(self.mpvExists()):
                self.mpvStop()
            else:
                self.speak_dialog("ytmpv.not.exists")
        except Exception as e:
            LOG.exception("YoutubeMpv Error: " + e.message)
            self.speak_dialog("ytmpv.error")

    @intent_handler(IntentBuilder("").require("YoutubeMpvVolume"))
    def handle_youtubempv_volume_intent(self, message):
        try:
            if(self.mpvExists()):
                msg = str(message.data.get("utterance")).split(" ")[2]
                self.speak_dialog(msg)
                if(msg == 'up'):
                    self.mpvChangeVol(self.volume+10)

                elif(msg == 'down'):
                    self.mpvChangeVol(self.volume-10)

                elif(msg != ''):
                    num = int(msg)
                    self.mpvChangeVol(num)
            else:
                self.speak_dialog("ytmpv.not.exists")
        except Exception as e:
            LOG.exception("YoutubeMpv Error: " + e.message)
            self.speak_dialog("ytmpv.error")

    # @intent_handler('stop.intent')
    # def handle_youtubempv_stop_intent(self, message):
    #     try:
    #         subprocess.call("killall mpv", shell=True)
    #     except Exception as e:
    #         LOG.exception("YoutubeMpv Error: " + e.message)
    #         self.speak_dialog("ytmpv.error")


def create_skill():
    return YoutubeMpvSkill()
