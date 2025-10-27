# 要匹配的哔哩哔哩直播间id（开发者方案的话不用这个）
ROOM_IDS = [
    # 21661347,
    # 23863287
]

# 这里填一个已登录账号的cookie的SESSDATA字段的值。不填也可以连接，但是收到弹幕的用户名会打码，UID会变成0
SESSDATA = ""

# 本地回复弹幕和tts
# 格式为 {"关键词1": "回复语音路径1", "关键词2": "回复语音路径2", ………}
SET_LOCAL_COMMENTS = {
    '1': './reply_audios/reply_nihao.mp3',
    '2': './reply_audios/runtime.wav'
}
