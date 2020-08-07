function invokeDevice(name, url) {
    var ba = new BootstrapAlert({
        dismissible: true,
        destroyAfter: 3000,
        max: 1
    });
    let msg;
    try {
        msg = document.getElementById(`text_${name}`).value;
      }
      catch(err) {
        msg = null;
      }
    ba.setBackground('success'); // set the alert to a success one
    if(msg){
        document.getElementById(`text_${name}`).value = '';
        sendWebRequest("GET",`${url}&msg=${msg}`);
        ba.addH(3, `Success! The device "${name}" is being invoked with this message: ${msg}`); // create a heading 1 tag
    } else {
        sendWebRequest("GET",`${url}`);
        ba.addH(3, `Success! The device "${name}" is being invoked.`); // create a heading 1 tag
    }
    document.getElementsByTagName('h1')[0].appendChild(ba.render());
}

function sendWebRequest(method,url){
    var xmlhttp = new XMLHttpRequest();

    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var myArr = JSON.parse(this.responseText);
            myFunction(myArr);
        }
    };
    xmlhttp.open(method, url, true);
    xmlhttp.send();
    console.log('sent!');
}