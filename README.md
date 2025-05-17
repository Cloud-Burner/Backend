# Backend
docker run --name Burner_base -e POSTGRES_USER=admin -e POSTGRES_PASSWORD=admin -e POSTGRES_DB=burner -p 5432:5432 -d postgres






ffmpeg -f v4l2 -i /dev/video0 \
  -c:v libx264 -preset ultrafast -tune zerolatency \
  -f hls -hls_time 1 -hls_list_size 3 -hls_flags delete_segments \
  /path/to/hls/stream.m3u8

WEBSOCKET_URL = "ws://192.168.1.39:8001/hls-upload"


pin rpi	pin green 
16	B8
20(gnd)	A6
22	B6
	
26	B7
28	A9
30	N6
32	A8
34	gnd left down
39(gnd)	gnd right down
13	A7
	
4	led
6	led

ssh -N -R 5173:localhost:5173 -R 8001:localhost:8001 <user>@cloudburner-miem.ru