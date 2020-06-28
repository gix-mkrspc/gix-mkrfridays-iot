function invokeDevice(name, url) {
    var ba = new BootstrapAlert({
        dismissible: true,
        destroyAfter: 3000,
        max: 1
    });
    ba.setBackground('success'); // set the alert to a success one
    ba.addH(3, `Success! The device "${name}" will be invoked.`); // create a heading 1 tag
    console.log(url);
    document.getElementsByTagName('h1')[0].appendChild(ba.render());
}