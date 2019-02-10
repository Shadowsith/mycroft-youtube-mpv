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
import urllib.request
from bs4 import BeautifulSoup
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.util.log import LOG

# Each skill is contained within its own class, which inherits base methods
# from the MycroftSkill class.  You extend this class as shown below.
# TODO: Change "Template" to a unique name for your skill


class YoutubeMpvSkill(MycroftSkill):
    # The constructor of the skill, which calls MycroftSkill's constructor
    def __init__(self):
        super(YoutubeMpvSkill, self).__init__(name="YoutubeMpvSkill")
        # Initialize working variables used within the skill.
        self.search = ""
        self.url = ""
        self.volume = 80

    def getResults(self, search, pos=0):
        query = urllib.parse.quote(search)
        link = "https://www.youtube.com/results?search_query=" + query
        response = urllib.request.urlopen(link)
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        vids = soup.findAll(attrs={'class': 'yt-uix-tile-link'})
        url = 'https://www.youtube.com' + vids[pos]['href']
        return url

    @intent_handler(IntentBuilder("").require("YoutubeMpv"))
    def handle_youtubempv_intent(self, message):
        try:
            msg = str(message.data.get('utterance')).split(" ")
            msg.pop(0)
            exists = subprocess.Popen("command -v mpv",
                                      stdout=subprocess.PIPE,
                                      shell=True).stdout.read()
            exists = exists.decode("utf-8")
            if(exists != ''):
                if(msg[0] == 'cancel'):
                    subprocess.call("killall mpv", shell=True)
                    self.speak_dialog("ytmpv.stop",
                                      data={"search": self.search})
                else:
                    self.search = " ".join(msg)
                    self.url = self.getResults(self.search)

                    subprocess.call(
                       "mpv --volume={} --input-ipc-server=/tmp/mpvsocket {} &"
                       .format(self.volume, self.url),
                       shell=True
                        )
                    self.speak_dialog("ytmpv.start",
                                      data={"search": self.search})
            else:
                self.speak_dialog("ytmpv.not.exists")
        except Exception as e:
            LOG.exception("mpv command failed")
            self.speak_dialog(e.message)


def create_skill():
    return YoutubeMpvSkill()
