nohup bokeh serve ReLIVE --allow-websocket-origin=* &
nohup python3 ReLIVE/flaskServer.py &
pwd_=`pwd`
sudo nginx -c $pwd_/ReLIVE/nginx.conf
