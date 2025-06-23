import rumps
import subprocess
import threading
import time
import webbrowser

FLASK_COMMAND = ['python3', 'main.py']

class GeneralAgentBarApp(rumps.App):
    def __init__(self):
        super(GeneralAgentBarApp, self).__init__("General Agent", icon="icon.icns", quit_button=True)
        self.flask_process = None

    @rumps.clicked("Start Server")
    def start_server(self, _):
        if self.flask_process and self.flask_process.poll() is None:
            rumps.alert("Server is already running.")
            return
        
        def run_flask():
            self.flask_process = subprocess.Popen(FLASK_COMMAND)
            self.flask_process.wait()
        
        threading.Thread(target=run_flask, daemon=True).start()
        rumps.notification("General Agent", "Server started", "Flask backend is up and running.")
    
    @rumps.clicked("Open UI")
    def open_ui(self, _):
        webbrowser.open("http://localhost:5000")

    @rumps.clicked("Stop Server")
    def stop_server(self, _):
        if self.flask_process and self.flask_process.poll() is None:
            self.flask_process.terminate()
            rumps.notification("General Agent", "Server stopped", "Flask backend has been terminated.")
        else:
            rumps.alert("Server is not running.")

if __name__ == "__main__":
    app = GeneralAgentBarApp()
    app.run()