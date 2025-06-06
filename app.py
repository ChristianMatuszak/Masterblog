import json

from flask import request, Flask, render_template, redirect

app = Flask(__name__)


def load_posts():
    """
    Loads all blog posts from the JSON storage file.
    This function reads the 'data/post.json' file and parses the content as JSON.
    It also performs a validation step to ensure all blog posts have unique IDs.
    If duplicate IDs are found, a ValueError is raised to prevent data conflicts.

    Returns:
        list[dict]: A list of blog posts, where each post is a dictionary
                    containing 'id', 'author', 'title', and 'content'.
    Raises:
        ValueError: If duplicate post IDs are detected in the data.
    """
    with open("data/post.json", "r") as file:
        posts = json.load(file)

    ids = [post["id"] for post in posts]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate IDs found in posts")

    return posts


@app.route('/')
def index():
    """
    Handles the home page route ('/') of the blog application.
    This function retrieves all blog posts from the storage file using `load_posts()`
    and renders the 'index.html' template, passing the list of posts to be displayed
    on the home page.

    Returns:
        str: Rendered HTML of the home page with all blog posts listed.
    """
    blog_posts = load_posts()
    return render_template("index.html", posts=blog_posts)


@app.route('/add', methods=['GET', 'POST'])
def add():
    """
    Handles the route for adding a new blog post ('/add').

    On a GET request, this function renders the 'add.html' template containing
    the post submission form. On a POST request, it processes the form data,
    assigns a new unique ID to the post, appends it to the existing list,
    and saves the updated list back to the JSON file. The user is then redirected
    to the home page.

    Returns:
        str or Response: The add post form page (GET), or a redirect response to the home page (POST).
    """
    if request.method == "POST":
        blog_posts = load_posts()
        new_id = get_next_id()

        while id_exists(new_id, blog_posts):
            new_id += 1

        new_post = {
            "id": get_next_id(),
            "author": request.form["author"],
            "title": request.form["title"],
            "content": request.form["content"],
        }

        blog_posts.append(new_post)

        with open("data/post.json", "w") as file:
            json.dump(blog_posts, file, indent=4)  # type: ignore
        return redirect("/")
    else:
        return render_template("add.html")


@app.route("/delete/<int:post_id>")
def delete(post_id):
    """
    Handles the deletion of a blog post by its ID.
    This function finds the blog post with the given "post_id", removes it
    from the "blog_posts" list, and saves the updated list back to the JSON file.
    Afterward, it redirects the user to the home page.

    Args:
        post_id (int): The ID of the blog post to be deleted.
    Returns:
        Response: A redirect response to the home page after deletion.
    """
    blog_posts = load_posts()
    blog_posts = [post for post in blog_posts if post["id"] != post_id]

    with open("data/post.json", "w") as file:
        json.dump(blog_posts, file, indent=4)  # type: ignore

    return redirect("/")


@app.route("/update/<int:post_id>", methods=["GET", "POST"])
def update(post_id):
    """
    Handles both GET and POST requests for updating a blog post.
    - GET: Retrieves the current blog post by "post_id" and show the update form.
    - POST: Updates the blog post with the new data from the form and redirects it.
    Args:
        post_id (int): The ID of the blog post to be updated.
    Returns:
        Response: Renders the update form (GET) or redirects to home (POST)
    """

    post = fetch_post_by_id(post_id)

    if post is None:
        return "Post not found", 404

    if request.method == "POST":
        post["author"] = request.form["author"]
        post["title"] = request.form["title"]
        post["content"] = request.form["content"]

        blog_posts = load_posts()

        for i, existing_post in enumerate(blog_posts):
            if existing_post["id"] == post_id:
                blog_posts[i] = post
                break

        with open("data/post.json", "w") as file:
            json.dump(blog_posts, file, indent=4)  # type: ignore

        return redirect("/")

    return render_template("update.html", post=post)


def get_next_id():
    """
    Calculates the next available unique ID for a new blog post.
    This function loads all existing blog posts and determines the highest
    existing ID. It returns the next consecutive integer as the new ID.
    If no posts exist, it returns 1 as the starting ID.

    Returns:
        int: The next available ID for a new post.
    """
    posts = load_posts()
    if posts:
        return max(post["id"] for post in posts) + 1
    return 1


def fetch_post_by_id(post_id):
    """
    Fetches a blog post by its ID.
    This function loads all blog posts and searches for the one with the
    specified ID. If found, it returns the post; otherwise, it returns None.

    Args:
        post_id (int): The ID of the blog post to fetch.
    Returns:
        dict or None: The blog post dictionary if found, None otherwise.
    """
    posts = load_posts()
    for post in posts:
        if post["id"] == post_id:
            return post
    return None


def id_exists(post_id, posts):
    """
    Checks if a given ID already exists in the list of blog posts.
    This utility function is used to ensure that each new post receives a
    unique ID. It searches through all posts to verify ID uniqueness.

    Args:
        post_id (int): The ID to check for existence.
        posts (list[dict]): A list of existing blog post dictionaries.
    Returns:
        bool: True if the ID already exists in the list, False otherwise.
    """
    return any(post["id"] == post_id for post in posts)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
