var os = require('os');
if (os.platform() == 'win32') {  
    var chilkat = require('chilkat_node6_win32'); 
} else if (os.platform() == 'linux') {
    if (os.arch() == 'arm') {
        var chilkat = require('chilkat_node6_arm');
    } else if (os.arch() == 'x86') {
        var chilkat = require('chilkat_node6_linux32');
    } else {
        var chilkat = require('chilkat_node6_linux64');
    }
} else if (os.platform() == 'darwin') {
    var chilkat = require('chilkat_node6_macosx');
}

function chilkatExample() {

    var mht = new chilkat.Mht();

    var success;

    success = mht.UnlockComponent("Anything for 30-day trial");
    if (success !== true) {
        console.log(mht.LastErrorText);
        return;
    }

    var mhtStr;

    mhtStr = mht.GetMHT("http://www.google.com/");
    if (mht.LastMethodSuccess !== true) {
        console.log(mht.LastErrorText);

    }
    else {
        console.log(mhtStr);
    }


}

chilkatExample();
