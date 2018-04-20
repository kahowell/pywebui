import argparse
import json
import os
import sys
from subprocess import Popen

from cookiecutter.main import cookiecutter
from cookiecutter.generate import generate_context
from cookiecutter.prompt import prompt_for_config

TEMPLATES_PATH = os.path.join(os.path.dirname(__file__), 'templates')

def create_project(args, _):
    context = generate_context(os.path.join(TEMPLATES_PATH, 'app', 'cookiecutter.json'))
    config = prompt_for_config(context)
    config['_app_dir'] = args.output_directory
    cookiecutter(os.path.join(TEMPLATES_PATH, 'app'), no_input=True, extra_context=config)
    os.chdir(args.output_directory)
    if not args.without_electron:
        cookiecutter(os.path.join(TEMPLATES_PATH, 'electron'), no_input=True, extra_context=config)
    if not args.without_cordova:
        cookiecutter(os.path.join(TEMPLATES_PATH, 'cordova'), no_input=True, extra_context=config)
    if not args.without_flask:
        cookiecutter(os.path.join(TEMPLATES_PATH, 'flask'), no_input=True, extra_context=config)

def shell(command):
    print('Command: ' + command)
    Popen(command, shell=True).wait()

def build_project(args, _):
    build_electron = False
    build_cordova = False
    if args.electron:
        build_electron = True
    if args.cordova:
        build_cordova = True
    if not args.electron and not args.cordova:
        build_electron = True
        build_cordova = True
    if not os.path.exists('package.json'):
        print('No package.json detected. Is this directory a PyWebUI project?')
        sys.exit(1)
    if not os.path.exists('node_modules'):
        shell('npm install')
    shell('npm run webpack')
    if os.path.exists('electron') and build_electron:
        print('Performing electron build from electron dir...')
        os.chdir('electron')
        if not os.path.exists('node_modules'):
            shell('npm install')
        shell('npm run dist')
        os.chdir('..')
    if os.path.exists('cordova') and build_cordova:
        print('Performing cordova build from cordova dir...')
        os.chdir('cordova')
        if not os.path.exists('node_modules'):
            shell('npm install')
        shell('cordova prepare')
        shell('cordova plugin add ./cordova-plugin-pywebui')
        shell('cordova build')
        os.chdir('..')
    print('Done. Build results are in their various folders.')

def main():
    parser = argparse.ArgumentParser(description='create/build a Python App with a Web UI-based GUI')
    commands = parser.add_subparsers(title='commands')

    create_command = commands.add_parser('create', help='create a new PyWebUI project')
    create_command.add_argument('--output-directory', help='where to output the project (default: app)', default='app')
    create_command.add_argument('--without-electron', help='include electron app', action='store_true')
    create_command.add_argument('--without-cordova', help='include cordova app', action='store_true')
    create_command.add_argument('--without-flask', help='include flask app', action='store_true')
    create_command.set_defaults(func=create_project)

    build_command = commands.add_parser('build', help='perform all builds for a PyWebUI project')
    build_command.add_argument('--electron', help='build for electron specifically', action='store_true')
    build_command.add_argument('--cordova', help='build for cordova specifically', action='store_true')
    build_command.set_defaults(func=build_project)

    args, remaining_args = parser.parse_known_args()
    args.func(args, remaining_args)


if __name__ == '__main__':
    main()