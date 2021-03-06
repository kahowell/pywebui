import argparse
import json
import os
import shutil
import sys
from subprocess import Popen, check_output

from cookiecutter.main import cookiecutter
from cookiecutter.generate import generate_context
from cookiecutter.prompt import prompt_for_config
import yaml

TEMPLATES_PATH = os.path.join(os.path.dirname(__file__), 'templates')

def create_project(args, _):
    context = generate_context(os.path.join(TEMPLATES_PATH, 'app', 'cookiecutter.json'))
    config = prompt_for_config(context)
    config['_app_dir'] = args.output_directory
    with open('.pywebui.yaml', 'w') as config_output:
        config_output.write(yaml.safe_dump(config, default_flow_style=False, encoding='utf-8'))
    cookiecutter(os.path.join(TEMPLATES_PATH, 'app'), no_input=True, extra_context=config)
    os.chdir(args.output_directory)
    if not args.without_electron:
        cookiecutter(os.path.join(TEMPLATES_PATH, 'electron'), no_input=True, extra_context=config)
    if not args.without_cordova:
        cookiecutter(os.path.join(TEMPLATES_PATH, 'cordova'), no_input=True, extra_context=config)
    if not args.without_flask:
        cookiecutter(os.path.join(TEMPLATES_PATH, 'flask'), no_input=True, extra_context=config)
    shell('npm install {} --no-save'.format(os.path.join(os.path.dirname(__file__), 'js')))

def _read_config():
    if not os.path.exists('.pywebui.yaml'):
        print('No .pywebui.yaml detected. Is this directory a PyWebUI project?')
        sys.exit(1)
    with open('.pywebui.yaml', 'r') as config_input:
        return yaml.load(config_input.read())

def update_project(args, _):
    config = _read_config()
    output_directory = args.output_directory or config['_app_dir']
    os.chdir(output_directory)
    for backend in args.remove:
        shutil.rmtree(backend)
    for backend in args.add:
        cookiecutter(os.path.join(TEMPLATES_PATH, backend), no_input=True, extra_context=config)
    print('Ensuring bridge JS up-to-date...')
    shell('npm install {} --no-save'.format(os.path.join(os.path.dirname(__file__), 'js')))

def shell(command, chdir=None, hide_output=False):
    print('Command: ' + command)
    if chdir:
        original_dir = os.getcwd()
        os.chdir(chdir)
    if hide_output:
        print('<output omitted>')
        with open(os.devnull, 'w') as output:
            Popen(command, shell=True, stdout=output)
    else:
        Popen(command, shell=True).wait()
    if chdir:
        os.chdir(original_dir)

def _get_bridge_requirement(file_protocol=''):
    try:
        installed_deps = check_output('pip freeze', shell=True).strip()
        lines = installed_deps.split('\n')
        for line in lines:
            if 'pywebui.bridge' in line:
                if '-e ' not in line:
                    return line
                else:
                    # track down file where dev version of bridge is stored
                    import pywebui.bridge
                    return '{}{}'.format(file_protocol, os.path.abspath(os.path.join(os.path.dirname(pywebui.bridge.__file__), '..', '..')))
    except:
        pass
    return 'pywebui.bridge'

def get_requirements(separator=' ', use_requirements_file=True, file_protocol=''):
    original_dir = os.getcwd()
    while not os.path.exists('.pywebui.yaml') and os.path.abspath('..') != os.path.abspath(os.getcwd()):
        os.chdir('..')
    if os.path.exists('requirements.txt'):
        print('Using requirements.txt for dependencies')
        requirements_path = 'requirements.txt'
    else:
        print('Using dependencies determined from setup.py')
        shell('python setup.py egg_info')
        package_name = check_output('python setup.py --name', shell=True).strip()
        requirements_path = '{}.egg-info/requires.txt'.format(package_name)
    if use_requirements_file:
        requirements = '-r {}'.format(requirements_path)
    with open(requirements_path, 'r') as requirements_file:
        lines = requirements_file.readlines()
        if not use_requirements_file:
            requirements = separator.join(line.strip() for line in lines if 'pywebui.bridge' not in line)
        if len([line for line in lines if line.startswith('pywebui.bridge')]) == 0:
            requirements = separator.join([requirements, _get_bridge_requirement()])
    requirements = separator.join(['{}{}'.format(file_protocol, os.getcwd()), requirements])
    os.chdir(original_dir)
    return requirements

def _build_cordova(config):
    original_path = os.getcwd()
    os.chdir(config['_app_dir'])
    print('Performing cordova build from cordova dir...')
    os.chdir('cordova')
    if not os.path.exists('node_modules'):
        shell('npm install')
    shell('cordova prepare')
    shell('cordova plugin add ./cordova-plugin-pywebui')
    shell('cordova build')
    os.chdir(original_path)

def _build_electron(config):
    original_path = os.getcwd()
    requirements_args = get_requirements()
    shell('pex --disable-cache {} -m pywebui.bridge -o {}'.format(requirements_args, os.path.join(config['_app_dir'], 'electron', 'app.pex')))
    print('Performing electron build from electron dir...')
    os.chdir(config['_app_dir'])
    os.chdir('electron')
    if not os.path.exists('node_modules'):
        shell('npm install')
    shell('npm run dist')
    os.chdir(original_path)

def build_project(args, _):
    original_dir = os.getcwd()
    config = _read_config()
    build_electron = args.electron or False
    build_cordova = args.cordova or False
    if not build_cordova and not build_electron:
        build_electron = os.path.exists('electron')
        build_cordova = os.path.exists('cordova')

    os.chdir(config['_app_dir'])
    if not os.path.exists('node_modules'):
        shell('npm install')
    shell('npm run webpack')
    os.chdir(original_dir)

    if build_electron:
        _build_electron(config)

    if build_cordova:
        _build_cordova(config)
        
    print('Done. Build results are in their various folders.')

def build_p4a(args, extra_args):
    p4a_src_dir = os.path.join(args.p4a_dir, 'src')
    requirements = ','.join(['python2', 'sdl2', 'six', get_requirements(separator=',', use_requirements_file=False, file_protocol='file://')])
    ARCHES = ['x86', 'armeabi-v7a']
    for arch in ARCHES:
        dist_name = 'pywebui-{}'.format(arch)
        if os.path.exists(os.path.join(args.p4a_dir, 'dist_{}'.format(arch))):
            print('Distribution already built for {}... Not rebuilding'.format(arch))
            continue
        print('Building python-for-android distribution for {}...'.format(arch))
        shell('python-for-android delete_dist {}'.format(dist_name), hide_output=True)
        shell('python-for-android apk --dist-name {dist_name} --arch {arch} --requirements {requirements}'.format(dist_name=dist_name, arch=arch, requirements=requirements), chdir=p4a_src_dir)
        shell('python-for-android export_dist --dist-name {dist_name} --arch {arch} dist_{arch} --requirements {requirements}'.format(dist_name=dist_name, arch=arch, requirements=requirements), chdir=args.p4a_dir)

def main():
    parser = argparse.ArgumentParser(description='create/build a Python App with a Web UI-based GUI')
    commands = parser.add_subparsers(title='commands')

    create_command = commands.add_parser('create', help='create a new PyWebUI project')
    create_command.add_argument('--output-directory', help='where to output the project (default: app)', default='app')
    create_command.add_argument('--without-electron', help='include electron app', action='store_true')
    create_command.add_argument('--without-cordova', help='include cordova app', action='store_true')
    create_command.add_argument('--without-flask', help='include flask app', action='store_true')
    create_command.set_defaults(func=create_project)

    update_command = commands.add_parser('update', help='update a PyWebUI project')
    update_command.add_argument('--output-directory', help='PyWebUI sub-project directory (default: detect)')
    update_command.add_argument('--add', nargs='+', help='add one or more backends', default=[])
    update_command.add_argument('--remove', '--rm', nargs='+', help='remove one or more backends', default=[])
    update_command.set_defaults(func=update_project)

    build_command = commands.add_parser('build', help='perform all builds for a PyWebUI project')
    build_command.add_argument('--electron', help='build for electron specifically', action='store_true')
    build_command.add_argument('--cordova', help='build for cordova specifically', action='store_true')
    build_command.set_defaults(func=build_project)

    build_p4a_command = commands.add_parser('build-p4a', help='build a python-for-android distribution (called internally)')
    build_p4a_command.add_argument('--p4a-dir', help='directory for the p4a directory')
    build_p4a_command.set_defaults(func=build_p4a)

    help_command = commands.add_parser('help', help='show this help')
    help_command.set_defaults(func=lambda args, extra_args: parser.print_help())

    args, remaining_args = parser.parse_known_args()
    args.func(args, remaining_args)


if __name__ == '__main__':
    main()