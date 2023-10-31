import datetime
import markdown2
import os
from pypinyin import lazy_pinyin
from markupsafe import Markup


class Post:
  def __init__(self, post_path, category=""):
    self._post_path = post_path
    self._local_category = category
    self._frontmatter = {}
    self._html = ""
    self._raw_md = ""
    # 确保文件存在
    self._check()
    # 解析文章内容，markdown 转换为 html
    self._parse_post()

  def __str__(self):
    return f"<Post {self._post_path}>"

  def __dict__(self):
    return self.serialize()

  def __iter__(self):
    return iter(self.serialize().items())

  def _check(self):
    if not os.path.exists(self._post_path):
      raise Exception('文件不存在')

    if not os.path.isfile(self._post_path):
      raise Exception('不是文件')

  def raw_md(self):
    """
    返回文章的 markdown 内容
    """
    return self._raw_md

  def frontmatter(self):
    """
    返回文章的 frontmatter 信息
    """
    return self._frontmatter

  def _parse_post(self):
    """
    解析文章内容，markdown 转换为 html
    在其中给三个属性赋值
    :return:
    """

    with open(self._post_path, 'r', encoding='utf-8') as f:
      raw_content = f.read().strip()

    # 读取文件最上面的 frontmatter，以 --- 开头，以 --- 结尾，截取之间的内容
    # TODO 改为支持多个分隔符的 frontmatter
    content_parts = raw_content.split("---")
    frontmatter = {}
    frontmatter["title"] = os.path.basename(self._post_path).replace(".md", "")
    frontmatter["date"] = datetime.datetime.now().strftime("%Y-%m-%d")
    frontmatter["category"] = self._local_category
    pinyin_title = lazy_pinyin(frontmatter["title"])
    slug = "-".join(pinyin_title)
    frontmatter["slug"] = slug

    if len(content_parts) > 2 and content_parts[0].strip() == "":
      # 读取 frontmatter
      frontmatter_str = content_parts[1].strip()
      # 解析 frontmatter，转换为字典
      for line in frontmatter_str.split("\n"):
        if line.strip() == "":
          continue
        key, value = line.split(":")
        frontmatter[key.strip()] = value.strip()

    self._frontmatter = frontmatter
    # 读取正文，并转换成 html。> 2 的情况下，说明有 frontmatter
    if len(content_parts) > 2:
      content = content_parts[2].strip()
    else:
      content = raw_content

    self._raw_md = content
    self._html = markdown2.markdown(content)

  def serialize(self):
    return {
      'post_path': self._post_path,
      'category': self.category(),
      'date': self.date,
      'title': self.title,
      'html': self._html,
      'raw_md': self._raw_md
    }

  @property
  def title(self):
    return self._frontmatter.get('title', '')

  def category(self):
    return self._frontmatter.get('category', '')

  @property
  def date(self):
    return self._frontmatter.get('date', '')

  @property
  def slug(self):
    return self._frontmatter.get('slug', '')

  @property
  def path(self):
    return f"/posts/{self.category()}/{self.slug}"

  @property
  def html_content_render(self):
    """
    返回文章的 markdown 转换为 html 的内容
    """
    return Markup(self._html)

  @property
  def html_content(self):
    """
    返回文章的 markdown 转换为 html 的内容
    """
    return self._html
