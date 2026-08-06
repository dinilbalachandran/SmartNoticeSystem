from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/faculty")
def faculty():
    return render_template("faculty.html")

@app.route("/notice-sources")
def notice_sources():
    return render_template("notice_sources.html")

if __name__ == "__main__":
    app.run(debug=True)