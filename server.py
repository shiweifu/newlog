import time
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from flask import Flask, jsonify, render_template

from app.engine import Engine

engine = None


def run():
  global engine
  try:
    engine = Engine("tmp_data")
  except Exception as e:
    print(e)
    exit(1)

  watch("./tmp_data")
  server()


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
    return render_template("archive.html",
                           categories=engine.get_categories())

  @app.route("/api/posts", methods=["GET"])
  def get_posts():
    return jsonify([dict(post) for post in engine._posts])

  @app.route("/")
  def index():
    return render_template("index.html", posts=engine.get_posts())

  app.run(debug=True, port=7000)


class MyHandler(FileSystemEventHandler):

  def __init__(self):
    self._last_trigger_time = time.time()

  def process(self):
    global engine
    engine.reload_data()

  def on_modified(self, event):
    if event.is_directory:
      return

    current_time = time.time()
    if event.src_path.find('~') == -1 and (current_time - self._last_trigger_time) > 1:
      self._last_trigger_time = current_time
      self.process()

  def on_deleted(self, event):
    if event.is_directory:
      return

    if event.src_path.find('~') == -1:
      self.process()


def watch(path="data"):
  event_handler = MyHandler()
  observer = Observer()
  observer.schedule(event_handler, path, recursive=True)
  observer.start()
