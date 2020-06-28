function invokeDevice(name, url) {
    var ba = new BootstrapAlert({
        dismissible: true,
        destroyAfter: 3000,
        max: 1
    });
    let msg = document.getElementById(`text_${name}`).value;
    ba.setBackground('success'); // set the alert to a success one
    if(msg){
        document.getElementById(`text_${name}`).value = '';
        ba.addH(3, `Success! The device "${name}" will be invoked with this message: ${msg}`); // create a heading 1 tag
    } else {
        ba.addH(3, `Success! The device "${name}" will be invoked.`); // create a heading 1 tag
    }
    document.getElementsByTagName('h1')[0].appendChild(ba.render());
}