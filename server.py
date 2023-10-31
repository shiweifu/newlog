import time
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from flask import Flask, jsonify, render_template

from app.engine import Engine

engine: Engine | None = None


def run():
  global engine
  try:
    engine = Engine("./tmp_data")
  except Exception as e:
    print(e)
    exit(1)

  watch("./tmp_data")
  server()


def server():
  global engine
  #   run a flask web server
  app = Flask(__name__)

  @app.context_processor
  def inject_title():
    # 在此处获取默认标题值的逻辑，可以从配置文件中读取，或者动态生成
    default_title = engine.config["site"]["title"]
    # 返回一个字典，包含要在所有模板中使用的默认标题
    return {'default_title': default_title}

  @app.route("/api/posts/<string:slug>", methods=["GET"])
  def get_post(slug):
    post = engine.get_post(slug)
    if post:
      return jsonify(dict(post))
    else:
      return jsonify({"error": "文章不存在"}), 404

  @app.route("/api/posts", methods=["GET"])
  def get_posts():
    return jsonify([dict(post) for post in engine.get_posts()])

  @app.route("/archive", methods=["GET"])
  def archive():
    posts = engine.get_posts()
    return render_template("archive.html",
                           posts=posts,
                           n="归档")

  @app.route("/")
  def index():
    return render_template("index.html",
                           categories=engine.get_categories())

  @app.route("/posts/<string:category>/<string:slug>", methods=["GET"])
  def get_post_page(category, slug):
    post = engine.get_post(slug, category)
    if post:
      return render_template("post.html", post=post)
    else:
      return jsonify({"error": "文章不存在"}), 404

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
