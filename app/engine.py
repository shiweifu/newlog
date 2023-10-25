import os
import yaml

from models.post import Post


class Engine:
  def __init__(self, data_path='data'):
    self._categories = []
    self._posts = []
    self._config = {}
    # key: category, value: posts
    self._categories_and_posts = {}
    self._data_path = data_path + "/posts"
    self._check()
    self._load_config()
    self.generate_blog_data()

  def _load_config(self):
    # 读取 config.yaml 文件，解析其中内容作为配置
    cfg_path = self._data_path + "/config.yaml"
    if os.path.exists(cfg_path):
      with open(cfg_path, 'r', encoding='utf-8') as f:
        cfg_content = f.read().strip()
        # 使用 pyyaml 库解析 yaml 文件
        cfg = yaml.load(cfg_content, Loader=yaml.FullLoader)
        cfg["site_title"] = cfg["site_title"] if "site_title" in cfg.keys() else "My Blog"
        cfg["site_description"] = cfg["site_description"] if "site_description" in cfg.keys() else ""

        self._config = cfg
        print("asdf")

  def categories(self):
    return self._categories

  def posts(self):
    return self._posts

  def categories_and_posts(self):
    return self._categories_and_posts

  def get_post(self, post_id):
    post = next((post for post in self._posts if post.id == post_id), None)
    if post:
      return post
    else:
      return None

  def generate_blog_data(self):
    # 遍历分类目录，生成分类数据，data下的所有文件夹，均为分类
    for category_name in os.listdir(self._data_path):
      self._categories.append(category_name)
      category_path = self._data_path + "/" + category_name
      if os.path.isdir(category_path):
        # 便利目录下的文件
        for post_name in os.listdir(category_path):
          if post_name.endswith(".md"):
            # 生成文章数据
            full_post_path = category_path + "/" + post_name
            post = Post(full_post_path, category_name)
            # 将文章数据添加到分类数据中
            self._posts.append(post)
          else:
            # TODO 改为打日志
            print("文件不存在")
    self._reload_categories_and_posts()

  def _check(self):
    pass

  def _clean(self):
    self._categories = []
    self._posts = []
    self._categories_and_posts = {}

  def reload_data(self):
    self._clean()
    self._load_config()
    self.generate_blog_data()

  def _reload_categories_and_posts(self):
    # 遍历所有 posts，将文章数据添加到分类和文章数据中
    for post in self._posts:
      if post.category() in self._categories_and_posts.keys():
        self._categories_and_posts[post.category()].append(post)
      else:
        self._categories_and_posts[post.category()] = [post]
    self._categories = list(self._categories_and_posts.keys())