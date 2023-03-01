from re import search, RegexFlag

from pydoc_markdown.interfaces import Context
from pydoc_markdown.contrib.loaders.python import PythonLoader
from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer, MarkdownReferenceResolver
from pydoc_markdown.contrib.processors.filter import FilterProcessor

"""
This script:
- Extracts & renders docstrings from helpers & escape_helpers
- Inserts that render into README.md in the right position, replacing the previous docstrings but nothing else
"""

def open_readme(mode="r"):
    return open("README.md", mode=mode, encoding="UTF-8")

if __name__ == "__main__":

    context = Context(directory=".")
    loader = PythonLoader(modules=["helpers", "escape_helpers"])
    renderer = MarkdownRenderer(render_module_header=False, insert_header_anchors=True, code_headers=True, render_typehint_in_data_header=True, docstrings_as_blockquote=True)

    loader.init(context)
    renderer.init(context)

    # https://github.com/ahopkins/mayim/blob/main/build_api_docs.py#L256
    modules = list(loader.load())

    resolver = MarkdownReferenceResolver()

    # https://github.com/NiklasRosenstein/pydoc-markdown/discussions/263#discussioncomment-3409760
    processor = FilterProcessor()
    processor.process(modules, resolver=resolver)

    doc_string = renderer.render_to_string(modules)


    with open_readme("r") as readme:
        old_contents = readme.read()
        to_replace = search(r"### Helper methods((.|\n)*?)^###[^#]", old_contents, RegexFlag.MULTILINE).group(1)


        new_contents = old_contents.replace(to_replace, "\n" + doc_string)

    with open_readme("w") as readme:
        readme.write(new_contents)
        

