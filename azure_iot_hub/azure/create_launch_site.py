from yattag import Doc
import csv
import os
import pickle

doc, tag, text = Doc().tagtext()

FILE_PATH = 'device_function_urls.csv'

# HTML markup variables
TITLE = "GIX IoT Hub"
IMAGES = {
    'porg': "https://images-na.ssl-images-amazon.com/images/I/917jytDQwJL"
            "._AC_SL1500_.jpg",
    'screen': "https://images-na.ssl-images-amazon.com/images/I/51b9oSYE-rL.jpg",
    'servo': "https://images-na.ssl-images-amazon.com/images/I/515cu4qXTrL"
             "._AC_SL1100_.jpg",
    'blink': "https://images-na.ssl-images-amazon.com/images/I/71JLez8iW5L"
             "._AC_SL1002_.jpg",
    'Generic': "https://images-na.ssl-images-amazon.com/images/I/61W7jyyhFxL"
               "._AC_SL1200_.jpg"
    }
# Get devices
try:
    DEVICES = pickle.load(open("devices.pickle", "rb"))
except (OSError, IOError) as e:
    print('Could not find devices to create HTML template from!')


def create_card(device_name, device_id, device_type, url, img):
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
                    if(device_type == "screen"):
                        text(f"Send a message?")
                        doc.stag(
                            'input',
                            type='text',
                            id=f'text_{device_id}')
                    with tag(
                            'button',
                            klass='btn btn-primary',
                            id='activatebutton',
                            onclick=f"invokeDevice('{device_id}'"
                                    f",'{url}')"):
                        text(f"Activate {device_name}'s {device_type}")


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
    doc.asis('<script src="bootstrap-alerts.js"></script>')
    doc.asis('<script src="deviceScripts.js"></script>')
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
                for d in DEVICES:
                    device = DEVICES[d]
                    create_card(
                        device_name=device.name,
                        device_id=device.device_name,
                        device_type=device.kind,
                        url=device.function_url,
                        img=IMAGES[device.kind])


doc.asis(
    '<script src="https://code.jquery.com/jquery-3.2.1.slim.min.js"'
    'integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/'
    'GpGFF93hXpG5KkN" crossorigin="anonymous"></script>')
doc.asis(
    '<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9'
    '/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/'
    'ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>')
doc.asis(
    '<script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/'
    'js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/'
    'JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous">'
    '</script>')
print(doc.getvalue())

if not os.path.exists('generated_site'):
    os.mkdir('generated_site')

# TODO: use Path lib
with open("./generated_site/index.html", 'w') as html_file:
    # with open("./assets/generated_site/index.html", 'w') as html_file:
    html_file.write(doc.getvalue())
