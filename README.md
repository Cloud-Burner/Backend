# Backend
docker run --name Burner_base -e POSTGRES_USER=admin -e POSTGRES_PASSWORD=admin -e POSTGRES_DB=burner -p 5432:5432 -d postgres






ffmpeg -f v4l2 -i /dev/video0 \
  -c:v libx264 -preset ultrafast -tune zerolatency \
  -f hls -hls_time 1 -hls_list_size 3 -hls_flags delete_segments \
  /path/to/hls/stream.m3u8

WEBSOCKET_URL = "ws://192.168.1.39:8001/hls-upload"