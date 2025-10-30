import PyInstaller.__main__
from main import Main
import pygount
import shutil
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'True'


def create_project_summary():
    print('creating project summary...')
    os.system('pygount --format=summary --suffix=py,json,mp3,wav --duplicates --folders-to-skip=temp,.* --names-to-skip=project_summary.txt --out=project_summary.txt')
    with open('project_summary.txt', 'r', encoding='utf8') as file:
        data = file.read()
    print(data)

def create_executable():
    main = Main(main=False)
    game_name = main.game_name
    print('creating executable...' + (' (warning: testing mode enabled)' if main.testing else ''))
    PyInstaller.__main__.run(['main.py', '--onefile', '--noconsole', f'--name={game_name}', '--icon=data/assets/images/other/icon.ico', '--log-level=WARN'])
    clean_directory(game_name=game_name)

def clean_directory(game_name):
    try:
        shutil.move(src=f'dist/{game_name}.exe', dst=f'{game_name}.exe')
    except FileNotFoundError:
        print(f"the system cannot find the path specified: 'dist/{game_name}.exe'")
    try:
        shutil.rmtree(path='dist')
    except FileNotFoundError:
        pass
    try:
        shutil.rmtree(path='build')
    except FileNotFoundError:
        pass
    try:
        shutil.rmtree(path='__pycache__')
    except FileNotFoundError:
        pass
    try:
        os.remove(path=f'{game_name}.spec')
    except FileNotFoundError:
        pass
    print('executable created and directory cleaned up')

if __name__ == '__main__':
    create_project_summary()
    create_executable()
