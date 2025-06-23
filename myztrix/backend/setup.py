from setuptools import setup

APP = ['backend/run.py']
DATA_FILES = [
    ('assets', ['assets/myztrix_icon.icns']),
    # Optional: Add token.json/credentials.json if doing internal installs
    # ('MyztrixAgentData', ['backend/dev_config/token.json', 'backend/dev_config/credentials.json'])
]
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'assets/myztrix_icon.icns',
    'packages': [
        'flask',
        'google-auth',
        'google-auth-oauthlib',
        'google-api-python-client'
    ],
    'plist': {
        'CFBundleName': 'Myztrix Agent',
        'CFBundleDisplayName': 'MyztrixAgent',
        'CFBundleIdentifier': 'com.myztrix.agent',
        'CFBundleVersion': '0.1.0',
        'CFBundleShortVersionString': '0.1.0',
    },
    'includes': ['idna.idnadata'],  # Py2App fix for google-auth runtime crash
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)



