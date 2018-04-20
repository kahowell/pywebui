from pywebui.bridge import Bridge
from sys import stdin, stdout


if __name__ == '__main__':
    bridge = Bridge(stdin, stdout)
    bridge.run()