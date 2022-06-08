# returns list of attributes as a markdown
def get_bold_markdown(attributes: dict):
    markdown_str = ""
    for attr in attributes:
        markdown_str += "*" + attr + "* - " + str(attributes[attr]) + "\n"

    return markdown_str
