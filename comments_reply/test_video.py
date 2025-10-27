import time

import pygame

from config import SET_LOCAL_COMMENTS

cur_msg = '这个直播间是干啥的'
if cur_msg.strip() in SET_LOCAL_COMMENTS.keys():
    time.sleep(0.1)
    pygame.mixer.init()
    pygame.mixer.music.load(SET_LOCAL_COMMENTS[cur_msg.strip()])
    pygame.mixer.music.play()
    # 等待播放完成或用户中断
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)