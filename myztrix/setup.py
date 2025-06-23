from setuptools import setup

APP = ['run_agent.py']
DATA_FILES = []

OPTIONS = {
    'argv_emulation': True,
    'includes': [
        'idna.idnadata',
        'nltk',
        'nltk.data',
        'nltk.corpus',
        'nltk.tokenize',
    ],
    'packages': [
        'nltk',
        'requests',
        'flask',
        'google_auth_oauthlib',
        'googleapiclient',
        'apscheduler',
        'watchdog',
        'email_validator',
    ],
    'excludes': [
        'tkinter',
        'PyQt5',
        'PySide2',
        'pytest',
        'unittest',
    ],
    'plist': {
        'CFBundleName': 'MyztrixAgent',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'CFBundleIdentifier': 'com.myztrix.agent',
    },
}

setup(
    app=APP,
    name='MyztrixAgent',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

setup(
    app=APP,
    name='MyztrixAgent',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
