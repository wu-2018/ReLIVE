import argparse
import os
parser = argparse.ArgumentParser(description="*****Welcome!*****")
parser.add_argument('subcommand', choices=['start','stop'],
                    help='start or stop')

parser.add_argument('--port', type=int, nargs='*', default=[5006,8080],
                   help='specify the ports')
 
args = parser.parse_args()
if args.subcommand == 'start':
    ports = args.port
    if len(ports) != 2 or len(set(ports)) != 2:
         parser.error('Please give two different values!')
    ports = tuple(ports+[ports[1]])
    sh1 ='''nohup bokeh serve ./ReLIVE --show --port %s --args "http://localhost:%s" &
            bokeh_PID=$!
            nohup python3 ./ReLIVE/flaskServer.py %s &
            flask_PID=$!
            echo $bokeh_PID $flask_PID >./ReLIVE/.pid'''%ports
    os.system(sh1)
else:
    os.system('echo stop')
    os.system('kill `cat ./ReLIVE/.pid`;rm ./ReLIVE/.pid')
