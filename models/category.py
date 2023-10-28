class Category:
  def __init__(self, title, posts=None):
    if posts is None:
      posts = []
    self.title = title
    self.posts = posts
