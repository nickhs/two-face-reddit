var casper = require('casper').create({
  verbose: true,
  logLevel: 'debug',
  pageSettings: {
    javascriptEnabled: true,
    loadImages: true,
    loadPlugins: true,
    localToRemoteUrlAccessEnabled: true,
    userAgent: "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
  },
  safeLogs: false,
});

var global_return = null;

function handleImage(data) {
  var fd = new FormData();
  fd.append('image', data);
  
  var xhr = new XMLHttpRequest();
  if (!casper.cli.has('host')) {
    casper.die("No host defined!", 1);
  }
  xhr.open('POST', casper.cli.get("host"));
  var timeout = 60000;

  xhr.send(fd);

  var xhrCheck = setInterval(function() {
    if (xhr.responseText != '') {
      clearInterval(xhrCheck);
      clearTimeout(timed);
      global_return = xhr.responseText;
    } else {
      casper.echo("Nothing :(");
    }
  }, 5000);

  var timed = setTimeout(function() {
    clearInterval(xhrCheck);
    global_return = 'timeout';
  }, timeout);
}

casper.start('http://www.reddit.com/', function() {
  if (!this.cli.has('username')) {
    casper.die("You need to specify a username!", 1);
  }
  this.click("#header-bottom-right > span > a");
});

casper.waitFor(function check() {
    return false;
}, function then() {
}, function timeout() {
    var data = this.captureBase64('png', '.capimage');
    handleImage(data);
    
    var check = setInterval(function() {
      if (global_return != null) {
        clearInterval(check);
        casper.fill('form#login_reg', {
          'user': casper.cli.get('username'),
          'passwd': 'beagle',
          'passwd2': 'beagle',
          'captcha': global_return,
        }, true);
        casper.die("Done!", 0);
      }
    }, 5000);
}, 1000);

casper.run(function() {
  casper.log("Halted exit");
});
