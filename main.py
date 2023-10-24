from lib.engine import Engine
from flask import Flask, jsonify, request, render_template


def run():
  global engine
  try:
    engine = Engine("tmp_data")
  except Exception as e:
    print(e)


def server():
  #   run a flask web server
  app = Flask(__name__)

  @app.route("/api/posts/<int:post_id>", methods=["GET"])
  def get_post(post_id):
    post = next((post for post in engine._posts if post.id == post_id), None)
    if post:
      return jsonify(dict(post))
    else:
      return jsonify({"error": "文章不存在"}), 404

  @app.route("/archive", methods=["GET"])
  def archive():
    print(engine.categories())
    return render_template("archive.html",
                           categories=engine.categories(),
                           categories_and_posts=engine.categories_and_posts())

  @app.route("/api/posts", methods=["GET"])
  def get_posts():
    return jsonify([dict(post) for post in engine._posts])

  @app.route("/")
  def index():
    return render_template("index.html", posts=engine._posts)

  app.run(debug=True, port=5050)


if __name__ == '__main__':
  run()
  server()
