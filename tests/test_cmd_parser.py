# -*- coding: utf-8 -*-
from resources.lib.tubecast.youtube.utils import Command, CommandParser

# Chunk containing: "c", "S", "loungeStatus", "getNowPlaying"
cmd_bind_info = '461\n[[0,["c","cid","",8]\n]\n,[1,["S","sid"]]\n,[2,["loungeStatus",{"devices":"[{\\"app\\":\\"kodi-tubecast\\",\\"capabilities\\":\\"que,mus\\",\\"clientName\\":\\"unknown\\",\\"experiments\\":\\"\\",\\"name\\":\\"Kodi (kodi)\\",\\"id\\":\\"id\\",\\"type\\":\\"LOUNGE_SCREEN\\",\\"hasCc\\":\\"true\\"}]","connectionEventDetails":"{\\"deviceId\\":\\"id\\"}"}]]\n,[3,["getNowPlaying"]]\n]\n'
cmd_remote_connected = '550\n[[6,["remoteConnected",{"app":"android-phone","pairingType":"dial","capabilities":"que,atp,mus","ui":"true","clientName":"android","experiments":"","name":"name","remoteControllerUrl":"","id":"id","type":"REMOTE_CONTROL","device":"{\\"app\\":\\"android-phone\\",\\"pairingType\\":\\"dial\\",\\"capabilities\\":\\"que,atp,mus\\",\\"clientName\\":\\"android\\",\\"experiments\\":\\"\\",\\"name\\":\\"name\\",\\"remoteControllerUrl\\":\\"\\",\\"id\\":\\"id\\",\\"type\\":\\"REMOTE_CONTROL\\"}"}]]\n]\n'
cmd_remote_disconnected = '554\n[[79,["remoteDisconnected",{"app":"android-phone-14.21.54","pairingType":"dial","capabilities":"que,atp,mus","ui":"true","clientName":"android","experiments":"","name":"name","remoteControllerUrl":"","id":"id","type":"REMOTE_CONTROL","device":"{\\"app\\":\\"android-phone\\",\\"pairingType\\":\\"dial\\",\\"capabilities\\":\\"que,atp,mus\\",\\"clientName\\":\\"android\\",\\"experiments\\":\\"\\",\\"name\\":\\"name\\",\\"remoteControllerUrl\\":\\"\\",\\"id\\":\\"id\\",\\"type\\":\\"REMOTE_CONTROL\\"}"}]]\n]\n'


def test_bind_cmds():
    cmds = CommandParser(cmd_bind_info).get_commands()
    assert cmds == (
        Command(0, "c", ("cid", "", 8)),
        Command(1, "S", "sid"),
        Command(2, "loungeStatus", {
            "devices": "[{\"app\":\"kodi-tubecast\",\"capabilities\":\"que,mus\",\"clientName\":\"unknown\",\"experiments\":\"\",\"name\":\"Kodi (kodi)\",\"id\":\"id\",\"type\":\"LOUNGE_SCREEN\",\"hasCc\":\"true\"}]",
            "connectionEventDetails": "{\"deviceId\":\"id\"}"
        }),
        Command(3, "getNowPlaying", None),
    )

    cmds = CommandParser(cmd_remote_connected).get_commands()
    assert cmds == (
        Command(6, "remoteConnected", {
            "app": "android-phone", "pairingType": "dial", "capabilities": "que,atp,mus", "ui": "true",
            "clientName": "android", "experiments": "", "name": "name", "remoteControllerUrl": "", "id": "id",
            "type": "REMOTE_CONTROL",
            "device": "{\"app\":\"android-phone\",\"pairingType\":\"dial\",\"capabilities\":\"que,atp,mus\",\"clientName\":\"android\",\"experiments\":\"\",\"name\":\"name\",\"remoteControllerUrl\":\"\",\"id\":\"id\",\"type\":\"REMOTE_CONTROL\"}"
        }),
    )

    cmds = CommandParser(cmd_remote_disconnected).get_commands()
    assert cmds == (
        Command(79, "remoteDisconnected", {
            "app": "android-phone-14.21.54", "pairingType": "dial", "capabilities": "que,atp,mus", "ui": "true",
            "clientName": "android", "experiments": "", "name": "name", "remoteControllerUrl": "", "id": "id",
            "type": "REMOTE_CONTROL",
            "device": "{\"app\":\"android-phone\",\"pairingType\":\"dial\",\"capabilities\":\"que,atp,mus\",\"clientName\":\"android\",\"experiments\":\"\",\"name\":\"name\",\"remoteControllerUrl\":\"\",\"id\":\"id\",\"type\":\"REMOTE_CONTROL\"}"
        }),
    )


# 3 commands in a single chunk
cmd_get_state = '71\n[[7,["getNowPlaying"]]\n,[8,["getSubtitlesTrack"]]\n,[9,["getVolume"]]\n]\n'
cmd_noop = '18\n[[20,["noop"]\n]\n]\n'
cmd_on_user_activity = '27\n[[21,["onUserActivity"]]\n]\n'
cmd_set_autoplay_mode = '55\n[[31,["setAutoplayMode",{"autoplayMode":"ENABLED"}]]\n]\n'


def test_misc_cmds():
    cmds = CommandParser(cmd_get_state).get_commands()
    assert cmds == (
        Command(7, "getNowPlaying", None),
        Command(8, "getSubtitlesTrack", None),
        Command(9, "getVolume", None),
    )

    cmds = CommandParser(cmd_noop).get_commands()
    assert cmds == (
        Command(20, "noop", None),
    )

    cmds = CommandParser(cmd_on_user_activity).get_commands()
    assert cmds == (
        Command(21, "onUserActivity", None),
    )

    cmds = CommandParser(cmd_set_autoplay_mode).get_commands()
    assert cmds == (
        Command(31, "setAutoplayMode", {"autoplayMode": "ENABLED"}),
    )


cmd_set_playlist = '634\n[[17,["setPlaylist",{"listId":"listid","currentTime":"0","ctt":"ctt","eventDetails":"{\\"videoId\\":\\"vid\\",\\"eventType\\":\\"VIDEO_ADDED\\",\\"userAvatarUri\\":\\"https://yt3.ggpht.com/a/default\\",\\"user\\":\\"user\\"}","sourceDeviceType":"REMOTE_CONTROL","clickTrackingParams":"","audioOnly":"false","videoId":"vid","playerParams":"","params":"","videoIds":"vid","currentIndex":"0"}]]\n]\n'
cmd_update_playlist = '403\n[[49,["updatePlaylist",{"listId":"listid","eventDetails":"{\\"videoId\\":\\"id\\",\\"eventType\\":\\"VIDEO_ADDED\\",\\"userAvatarUri\\":\\"https://yt3.ggpht.com/a/default\\",\\"user\\":\\"user\\"}","clickTrackingParams":"","audioOnly":"false","playerParams":"","params":"","videoIds":"vid,vid2"}]]\n]\n'
cmd_next = '17\n[[71,["next"]]\n]\n'
cmd_prev = '21\n[[74,["previous"]]\n]\n'


def test_playlist_cmds():
    cmds = CommandParser(cmd_set_playlist).get_commands()
    assert cmds == (
        Command(17, "setPlaylist", {
            "listId": "listid", "currentTime": "0", "ctt": "ctt",
            "eventDetails": "{\"videoId\":\"vid\",\"eventType\":\"VIDEO_ADDED\",\"userAvatarUri\":\"https://yt3.ggpht.com/a/default\",\"user\":\"user\"}",
            "sourceDeviceType": "REMOTE_CONTROL", "clickTrackingParams": "",
            "audioOnly": "false", "videoId": "vid", "playerParams": "", "params": "",
            "videoIds": "vid", "currentIndex": "0"
        }),
    )

    cmds = CommandParser(cmd_update_playlist).get_commands()
    assert cmds == (
        Command(49, "updatePlaylist", {
            "listId": "listid",
            "eventDetails": "{\"videoId\":\"id\",\"eventType\":\"VIDEO_ADDED\",\"userAvatarUri\":\"https://yt3.ggpht.com/a/default\",\"user\":\"user\"}",
            "clickTrackingParams": "", "audioOnly": "false", "playerParams": "", "params": "", "videoIds": "vid,vid2"
        }),
    )

    cmds = CommandParser(cmd_next).get_commands()
    assert cmds == (
        Command(71, "next", None),
    )

    cmds = CommandParser(cmd_prev).get_commands()
    assert cmds == (
        Command(74, "previous", None),
    )


cmd_pause = '18\n[[23,["pause"]]\n]\n'
cmd_play = '17\n[[25,["play"]]\n]\n'
cmd_seek_to = '36\n[[29,["seekTo",{"newTime":"56"}]]\n]\n'
cmd_set_volume = '49\n[[59,["setVolume",{"volume":"3","delta":"3"}]]\n]\n'


def test_player_cmds():
    cmds = CommandParser(cmd_pause).get_commands()
    assert cmds == (
        Command(23, "pause", None),
    )

    cmds = CommandParser(cmd_play).get_commands()
    assert cmds == (
        Command(25, "play", None),
    )

    cmds = CommandParser(cmd_seek_to).get_commands()
    assert cmds == (
        Command(29, "seekTo", {"newTime": "56"}),
    )

    cmds = CommandParser(cmd_set_volume).get_commands()
    assert cmds == (
        Command(59, "setVolume", {"volume": "3", "delta": "3"}),
    )
