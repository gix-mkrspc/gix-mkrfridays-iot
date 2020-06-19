from yattag import Doc

doc, tag, text = Doc().tagtext()

doc.asis('<!DOCTYPE html>')
with tag('html', lang="en"):
    with tag('body', id = 'hello'):
        doc.stag('meta', charset="utf-8")
        doc.stag(
            'meta',
            name="viewport",
            content="width=device-width, initial-scale=1, shrink-to-fit=no")
print(doc.getvalue())

# with open("index.html", 'w') as html_file:
#     html_file.write(doc.getvalue())
