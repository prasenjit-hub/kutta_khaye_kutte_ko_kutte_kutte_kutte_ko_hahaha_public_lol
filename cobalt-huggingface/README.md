---
title: Cobalt API
emoji: 🎬
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# Cobalt API - YouTube Video Downloader

This is a self-hosted Cobalt API instance for downloading YouTube videos with Hindi audio.

## API Endpoint

POST to `/` with JSON body:

```json
{
  "url": "https://youtube.com/watch?v=VIDEO_ID",
  "youtubeDubLang": "hi"
}
```

## Features

- Free to use
- No authentication required
- Hindi dubbed audio support
- 1080p video quality
