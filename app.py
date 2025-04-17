import json
from flask import Flask, render_template

app = Flask(__name__)

def load_posts():
    with open("post.json", "r") as file:
        return json.load(file)

@app.route('/')
def index():
    blog_posts = load_posts()
    return render_template("index.html", posts=blog_posts)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)