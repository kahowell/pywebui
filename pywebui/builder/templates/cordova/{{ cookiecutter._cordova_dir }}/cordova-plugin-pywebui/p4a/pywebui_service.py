import os
from pywebui.bridge import Bridge

if __name__ == '__main__':
    android_data_dir = os.environ['PYTHON_SERVICE_ARGUMENT']
    print('got android data dir ' + android_data_dir)
    with open(android_data_dir + '/pywebui.request.fifo', 'r') as bridge_in:
        with open(android_data_dir + '/pywebui.response.fifo', 'w') as bridge_out:
            bridge = Bridge(bridge_in, bridge_out)
            bridge.run()
