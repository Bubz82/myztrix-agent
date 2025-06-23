from setuptools import setup, find_packages

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
    name='cognee',
    version='0.1.42.post1',  # Marked as a patch release
    description='Cognee Agent',
    author='Cognee',
    author_email='support@cognee.com',
    packages=find_packages(),
    install_requires=[
        'requests',
        'fastapi>=0.115.7,<0.116.0',
        'pydantic>=2.0',
        'uvicorn',
        'python-multipart',
        'watchdog',
        'email_validator',
        'nltk',
        'apscheduler',
        'google-auth',
        'google-auth-oauthlib',
        'google-api-python-client',
        # Add any other hard deps here
    ],
    entry_points={
        'console_scripts': [
            'cognee=cognee.main:main',
        ],
    },
)
setup(
    app=APP,
    name='MyztrixAgent',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
