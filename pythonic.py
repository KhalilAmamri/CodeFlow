from flask import Flask, render_template, url_for

app = Flask(__name__)

lessons = [{
    "title": "Request Library Course",
    "course": "Python",
    "author" : "Khalil"
},
{
    "title": "Request-HTML Library Course",
    "course": "Python",
    "author" : "Omar"
},
{
    "title": "Datetime Module",
    "course": "Python",
    "author" : "mahdi"
}
]

@app.route("/")
def home():
    return render_template('home.html', lessons = lessons)

@app.route("/about")
def about():
    return render_template('about.html', title = "About Page")

if __name__== "__main__":
    app.run(debug=True)