## 哔站关键弹幕语音回复

### 依赖包

```shell
pip install -r requirements.txt
```

### 使用

#### 开发者方案（专用直播间）

1. 配置好关键弹幕预设（弹幕+回复语音）

- 在`bilibili_reply/comments_reply/reply_audios`文件夹里面存放设定好的回复语音，支持mp3和wav格式。
- 在`bilibili_reply/config.py`里面的配置关键词回复及映射。
  > `SET_LOCAL_COMMENTS = {"关键词1": "回复语音路径1", "关键词2": "回复语音路径2", ………}`

2. 配置好直播间信息
- 进入`bilibili_reply/comments_reply/open_live_run.py`，配置相关信息
  > ![img.png](https://coderethan-1327000741.cos.ap-chengdu.myqcloud.com/blog-pics/img.png)

3. 直接运行`bilibili_reply/comments_reply/open_live_run.py`

  > 注意要开播哈

