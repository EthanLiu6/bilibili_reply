# -*- coding: utf-8 -*-
import asyncio
import time
import os
import random
from concurrent.futures import ThreadPoolExecutor

import pygame

import blivedm
import blivedm.models.open_live as open_models
import blivedm.models.web as web_models
from config import SET_LOCAL_COMMENTS

# 在开放平台申请的开发者密钥
ACCESS_KEY_ID = 'xxx'
ACCESS_KEY_SECRET = 'xxx'
# 在开放平台创建的项目ID
APP_ID = ...
# 主播身份码
ROOM_OWNER_AUTH_CODE = 'xxx'

# 弹幕无回复播放随机音频的延时时间（秒）
NO_REPLY_DELAY_SECONDS = 15

# 全局线程池用于播放音频
_audio_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="audio_player")


async def main():
    await run_single_client()


async def run_single_client():
    """
    演示监听一个直播间
    """
    client = blivedm.OpenLiveClient(
        access_key_id=ACCESS_KEY_ID,
        access_key_secret=ACCESS_KEY_SECRET,
        app_id=APP_ID,
        room_owner_auth_code=ROOM_OWNER_AUTH_CODE,
    )
    handler = MyHandler()
    client.set_handler(handler)

    client.start()
    
    # 启动定时检查任务
    asyncio.create_task(handler._start_check_task())
    
    try:
        # 演示70秒后停止
        # await asyncio.sleep(70)
        # client.stop()

        await client.join()
    finally:
        await client.stop_and_close()


class MyHandler(blivedm.BaseHandler):
    def __init__(self):
        super().__init__()
        self.last_danmaku_time = time.time()  # 最后一条弹幕的时间，初始化为程序启动时间
        self.is_playing = False  # 是否正在播放音频
    
    async def _start_check_task(self):
        """启动定时检查任务"""
        await self._check_and_play_random()
    
    def _get_random_audios(self):
        """获取random_audios文件夹中的所有音频文件（wav, mp3, mp4）"""
        audio_dir = 'random_audios'
        if not os.path.exists(audio_dir):
            return []
        
        audio_files = []
        for file in os.listdir(audio_dir):
            if file.endswith(('.wav', '.mp3', '.mp4')):
                audio_files.append(os.path.join(audio_dir, file))
        return audio_files
    
    def _play_audio_sync(self, audio_path):
        """同步播放音频"""
        try:
            print(f"当前播放：{audio_path}")
            # 检查文件是否存在
            if not os.path.exists(audio_path):
                print(f'音频文件不存在: {audio_path}')
                return
            
            pygame.mixer.init()
            print(f"pygame.mixer已初始化")
            
            pygame.mixer.music.load(audio_path)
            print(f"音频文件已加载")
            
            pygame.mixer.music.play()
            print(f"开始播放音频")
            
            # 等待播放完成
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            print(f"播放完成")
        except Exception as e:
            print(f'播放音频失败: {e}')
            import traceback
            traceback.print_exc()
    
    async def _play_audio_async(self, audio_path):
        """异步播放音频"""
        if self.is_playing:
            print('正在播放音频，跳过')
            return
            
        self.is_playing = True
        try:
            # 使用全局线程池播放音频
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(_audio_executor, self._play_audio_sync, audio_path)
        finally:
            self.is_playing = False
    
    async def _play_random_audio(self):
        """播放random_audios文件夹中的随机音频"""
        audio_files = self._get_random_audios()
        print(f'查找random_audios文件夹，找到{len(audio_files)}个音频文件')
        if not audio_files:
            print('random_audios文件夹中没有找到音频文件')
            return
        
        # 随机选择一个音频文件
        audio_path = random.choice(audio_files)
        print(f'{NO_REPLY_DELAY_SECONDS}秒内无回复，播放随机音频: {audio_path}')
        await self._play_audio_async(audio_path)
    
    async def _check_and_play_random(self):
        """定期检查是否需要播放随机音频"""
        while True:
            try:
                await asyncio.sleep(1)  # 每秒检查一次
                
                # 如果正在播放音频，跳过
                if self.is_playing:
                    continue
                
                # 检查是否超过延时时间
                elapsed = time.time() - self.last_danmaku_time
                print(f"当前延时:{elapsed}")
                if elapsed >= NO_REPLY_DELAY_SECONDS:
                    print(f'超过{NO_REPLY_DELAY_SECONDS}秒无回复，播放随机音频')
                    # 先更新时间戳，避免重复触发
                    self.last_danmaku_time = time.time()
                    # 播放随机音频
                    await self._play_random_audio()
            except Exception as e:
                print(f'检查随机音频失败: {e}')
    
    def _on_heartbeat(self, client: blivedm.BLiveClient, message: web_models.HeartbeatMessage):
        print(f'[{client.room_id}] 心跳')

    def _on_open_live_danmaku(self, client: blivedm.OpenLiveClient, message: open_models.DanmakuMessage):
        print(f'[{message.room_id}] {message.uname}：{message.msg}')
        
        cur_msg = message.msg
        if cur_msg.strip() in SET_LOCAL_COMMENTS.keys():
            # 有匹配的弹幕，更新时间戳并播放音频
            self.last_danmaku_time = time.time()  # 有回复，重新计时
            
            audio_path = SET_LOCAL_COMMENTS[cur_msg.strip()]
            print(f'匹配到关键词，播放: {audio_path}')
            loop = asyncio.get_event_loop()
            loop.create_task(self._play_audio_async(audio_path))
        else:
            # 没有匹配的弹幕，更新时间戳
            self.last_danmaku_time = time.time()
            print(f'没有匹配的弹幕，更新最后弹幕时间: {time.strftime("%H:%M:%S", time.localtime())}')

    def _on_open_live_gift(self, client: blivedm.OpenLiveClient, message: open_models.GiftMessage):
        coin_type = '金瓜子' if message.paid else '银瓜子'
        total_coin = message.price * message.gift_num
        print(f'[{message.room_id}] {message.uname} 赠送{message.gift_name}x{message.gift_num}'
              f' （{coin_type}x{total_coin}）')

    def _on_open_live_buy_guard(self, client: blivedm.OpenLiveClient, message: open_models.GuardBuyMessage):
        print(f'[{message.room_id}] {message.user_info.uname} 购买 大航海等级={message.guard_level}')

    def _on_open_live_super_chat(
        self, client: blivedm.OpenLiveClient, message: open_models.SuperChatMessage
    ):
        print(f'[{message.room_id}] 醒目留言 ¥{message.rmb} {message.uname}：{message.message}')

    def _on_open_live_super_chat_delete(
        self, client: blivedm.OpenLiveClient, message: open_models.SuperChatDeleteMessage
    ):
        print(f'[{message.room_id}] 删除醒目留言 message_ids={message.message_ids}')

    def _on_open_live_like(self, client: blivedm.OpenLiveClient, message: open_models.LikeMessage):
        print(f'[{message.room_id}] {message.uname} 点赞')

    def _on_open_live_enter_room(self, client: blivedm.OpenLiveClient, message: open_models.RoomEnterMessage):
        print(f'[{message.room_id}] {message.uname} 进入房间')

    def _on_open_live_start_live(self, client: blivedm.OpenLiveClient, message: open_models.LiveStartMessage):
        print(f'[{message.room_id}] 开始直播')

    def _on_open_live_end_live(self, client: blivedm.OpenLiveClient, message: open_models.LiveEndMessage):
        print(f'[{message.room_id}] 结束直播')


if __name__ == '__main__':
    asyncio.run(main())
