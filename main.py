import os

from models.post import Post
from flask import Flask, jsonify, request, render_template


class Engine:
  def __init__(self, data_path='data'):
    self._categories = []
    self._posts = []
    self._data_path = data_path + "/posts"
    self._check()
    self.generate_blog_data()

  def generate_blog_data(self):
    # 遍历分类目录，生成分类数据，data下的所有文件夹，均为分类
    for category_name in os.listdir(self._data_path):
      # 打印 catagory 的名称
      category_path = self._data_path + "/" + category_name
      print(category_path)
      if os.path.isdir(category_path):
        # 便利目录下的文件
        for post_name in os.listdir(category_path):
          if post_name.endswith(".md"):
            # 生成文章数据
            full_post_path = category_path + "/" + post_name
            post = Post(full_post_path)
            # 将文章数据添加到分类数据中
            self._posts.append(post)
          else:
            # TODO 改为打日志
            print("文件不存在")

  def _check(self):
    if not os.path.exists(self._data_path):
      raise Exception('data 目录不存在')

    if not os.path.isdir(self._data_path):
      raise Exception('data 不是目录')


def run():
  global engine
  try:
    engine = Engine("tmp_data")
  except Exception as e:
    print(e)


def server():
  #   run a flask web server
  app = Flask(__name__)

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
