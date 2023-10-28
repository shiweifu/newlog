class Category:
  def __init__(self, title, posts=None):
    if posts is None:
      posts = []
    self._title = title
    self._posts = posts

  @property
  def title(self):
    return self._title

  @property
  def posts(self):
    return self._posts
