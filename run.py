import argparse
import os
import getIP
ip = getIP.getIP()

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
    sh1 ='''nohup bokeh serve ./ReLIVE --port {bokeh_port} --allow-websocket-origin={ip}:8000 --args "http://{ip}:8000" &
            bokeh_PID=$!
            uwsgi --ini ReLIVE/uwsgiconfig.ini
            nginx -c `pwd`"/ReLIVE/nginx.conf"
            echo $bokeh_PID >./ReLIVE/log/bokeh.pid'''
    os.system(sh1.format(bokeh_port=ports[0],ip=ip))
else:
    sh2 = '''
            echo stop
            kill `cat ./ReLIVE/log/bokeh.pid ./ReLIVE/log/nginx.pid`
            uwsgi --stop ./ReLIVE/log/uwsgi.pid
          '''
    os.system(sh2)
