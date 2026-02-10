from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Flask is alive"

if __name__ == "__main__":
    print("starting flask")
    app.run()
