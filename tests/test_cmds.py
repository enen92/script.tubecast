# -*- coding: utf-8 -*-
import sys
from resources.lib.tubecast.youtube.utils import parse_cmd

cmd_1 = '[[20,["remoteDisconnected",{"app":"android-phone-13.05.52","pairingType":"dial","capabilities":"atp,que,mus","ui":"true","clientName":"android","experiments":"","name":"MYPHONE","remoteControllerUrl":"ws://","id":"something","type":"REMOTE_CONTROL","device":"{\"app\":\"android-phone-13.05.52\",\"pairingType\":\"dial\",\"capabilities\":\"atp,que,mus\",\"clientName\":\"android\",\"experiments\":\"\",\"name\":\"MYPHONE\",\"remoteControllerUrl\":\"ws://\",\"id\":\"id\",\"type\":\"REMOTE_CONTROL\"}"}]]'
cmd_2 = '20,["remoteDisconnected",{"app":"android-phone-13.05.52","pairingType":"dial","capabilities":"atp,que,mus","ui":"true","clientName":"android","experiments":"","name":"MYPHONE","remoteControllerUrl":"ws://","id":"something","type":"REMOTE_CONTROL","device":"{\"app\":\"android-phone-13.05.52\",\"pairingType\":\"dial\",\"capabilities\":\"atp,que,mus\",\"clientName\":\"android\",\"experiments\":\"\",\"name\":\"MYPHONE\",\"remoteControllerUrl\":\"ws://\",\"id\":\"id\",\"type\":\"REMOTE_CONTROL\"}"}]]'


PY3 = sys.version_info.major >=3


def str_to_bytes(string):
    if PY3:
        return bytes(string, 'utf-8')
    return string


def test_cmd1():
    _, data = parse_cmd(str_to_bytes(cmd_1))
    assert data["name"] == "MYPHONE"


def test_cmd2():
    _, data = parse_cmd(str_to_bytes(cmd_2))
    assert data["name"] == "MYPHONE"
