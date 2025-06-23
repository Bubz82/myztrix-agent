from setuptools import setup

APP = ['run_agent.py']  # ✅ Entry point to your app — update if needed
DATA_FILES = []         # 📦 Add extra bundled files if needed
OPTIONS = {
    'argv_emulation': True,  # 👈 Needed for proper CLI args in macOS apps
    'includes': ['idna.idnadata'],  # 👈 Optional fix for macOS idna bug
    'packages': [
        'nltk',
        'requests',
        'flask',
        'google_auth_oauthlib',
        'googleapiclient',
        'apscheduler',
        'watchdog',
        'email_validator',
        'your_custom_modules',  # ⛔️ Replace/remove if not real
    ],
    'excludes': [
        'tkinter',        # 🚫 Drop unused GUI libs
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
