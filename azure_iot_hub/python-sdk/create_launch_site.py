from yattag import Doc
import csv

doc, tag, text = Doc().tagtext()

FILE_PATH = 'device_function_urls.csv'

# HTML markup variables
TITLE = "GIX IoT Hub"
PORG_IMG = "https://images-na." \
           "ssl-images-amazon.com/images/I/917jytDQwJL" \
           "._AC_SL1500_.jpg"


def create_card(device_name, device_type, url, img):
    with tag('div', klass='col-md'):
        with tag('div', klass='col card'):
            with tag('div', klass='row'):
                with tag('div', klass='col'):
                    doc.stag('img', src=img)
                with tag('div', klass='col'):
                    text(f'Name: {device_name}')
                    doc.asis('<br>')
                    text(f'Type: {device_type}')
            with tag('div', klass='row'):
                with tag('div', klass='col button'):
                    with tag(
                            'button',
                            klass='btn btn-primary',
                            id='activatebutton',
                            onclick=f"window.location.href='{url}'"):
                        text(f"Activate {device_type}")


doc.asis('<!DOCTYPE html>')
with tag('html', lang="en"):
    doc.stag('meta', charset="utf-8")
    doc.stag(
        'meta',
        name="viewport",
        content="width=device-width, initial-scale=1, shrink-to-fit=no")
    doc.stag(
        'link',
        rel='stylesheet',
        href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap"
             ".min.css",
        crossorigin="anonymous",
        integrity="sha384-"
        "Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm")
    doc.stag(
        'link',
        rel='stylesheet',
        href='style.css')
    with tag('title'):
        text(TITLE)
    with tag('body'):
        with tag('h1'):
            text(TITLE)
        with tag('div', klass='container'):
            with tag('div', klass='row'):
                with open(FILE_PATH, 'r', newline='') as csvfile:
                    reader = csv.reader(csvfile)
                    for row in reader:
                        create_card(
                            device_name=row[0],
                            device_type="Super Porg",
                            url=row[1],
                            img=PORG_IMG)

doc.asis('<script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>')
doc.asis('<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>')
doc.asis('<script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>')
print(doc.getvalue())

# TODO: use Path lib
with open("index.html", 'w') as html_file:
# with open("./assets/generated_site/index.html", 'w') as html_file:
    html_file.write(doc.getvalue())