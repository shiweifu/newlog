import os

import markdown2
import yaml
from markupsafe import Markup
from models.category import Category
from models.page import Page
from models.post import Post


class Engine:
  def __init__(self, data_path='data'):
    self._custom_css_content = ""
    self._custom_js_content = ""
    self._categories = []
    self._category_titles = []
    self._posts = []
    self._pages = []
    self._config = {}
    # key: category, value: posts
    self._categories_and_posts = {}
    self._posts_path = data_path + "/posts"
    self._data_path = data_path
    self._check()
    self._load_config()
    self.generate_blog_data()

  def _load_config(self):
    # 读取 config.yaml 文件，解析其中内容作为配置
    cfg_path = self._data_path + "/config.yaml"
    if not cfg_path.startswith("/"):
      cfg_path = f"{cfg_path}"
    if os.path.exists(cfg_path):
      with open(cfg_path, 'r', encoding='utf-8') as f:
        cfg_content = f.read().strip()
        # 使用 pyyaml 库解析 yaml 文件
        cfg = yaml.load(cfg_content, Loader=yaml.FullLoader)
        self._config = cfg

  def _check(self):
    pass

  def _clean(self):
    self._categories = []
    self._posts = []
    self._categories_and_posts = {}
    self._pages = []

  def reload_data(self):
    self._clean()
    self._load_config()
    self.generate_blog_data()

  def _reload_blog_data(self):
    # 遍历所有 posts，将文章数据添加到分类和文章数据中
    for post in self._posts:
      if post.category() in self._categories_and_posts.keys():
        self._categories_and_posts[post.category()].append(post)
      else:
        self._categories_and_posts[post.category()] = [post]

    #  将分类和文章数据转换为 Category 对象
    categories = []
    for category_name in self._categories_and_posts.keys():
      tmp_category = Category(category_name, self._categories_and_posts[category_name])
      categories.append(tmp_category)

    self._categories = categories
    self._category_titles = list(self._categories_and_posts.keys())

    pages = []
    pages_path = self._data_path + "/pages"
    if os.path.exists(pages_path):
      for page_name in os.listdir(pages_path):
        if page_name.endswith(".md"):
          page_path = pages_path + "/" + page_name
          page = Page(page_path)
          pages.append(page)
    self._pages = pages

  def get_categories(self):
    return self._categories

  def get_category_titles(self):
    return self._category_titles

  def get_posts(self):
    return self._posts

  def categories_and_posts(self):
    return self._categories_and_posts

  def get_post(self, slug, category=""):
    if category != "":
      post = next((post for post in self.categories_and_posts()[category] if post.slug == slug), None)
      if post:
        return post
      else:
        return None

    post = next((post for post in self._posts if post.slug == slug), None)
    if post:
      return post
    else:
      return None

  def generate_blog_data(self):
    # 遍历分类目录，生成分类数据，data下的所有文件夹，均为分类
    for category_name in os.listdir(self._posts_path):
      category_path = self._posts_path + "/" + category_name
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
    self._reload_blog_data()
    # 读取 custom_css 文件
    custom_css_path = self._data_path + "/custom.css"
    if os.path.exists(custom_css_path):
      with open(custom_css_path, 'r', encoding='utf-8') as f:
        self._custom_css_content = f.read().strip()
    # 读取 custom_js 文件
    custom_js_path = self._data_path + "/custom.js"
    if os.path.exists(custom_js_path):
      with open(custom_js_path, 'r', encoding='utf-8') as f:
        self._custom_js_content = f.read().strip()

  def get_page(self, slug):
    for page in self._pages:
      if page.page_name == slug:
        return page
    return None

  @property
  def config(self):
    return self._config

  @property
  def custom_css(self):
    return Markup(self._custom_css_content)

  @property
  def custom_js(self):
    return Markup(self._custom_js_content)
