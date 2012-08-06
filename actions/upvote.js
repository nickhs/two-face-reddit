var casper = require('casper').create({
  verbose: true,
  logLevel: 'debug',
  pageSettings: {
    javascriptEnabled: true,
    loadImages: true,
    loadPlugins: true,
    localToRemoteUrlAccessEnabled: true,
    userAgent: "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
    webSecurity: false,
  },
  safeLogs: false,
  viewportSize: {
    height: 800,
    width: 1280,
  }
});

casper.start('http://www.reddit.com/', function() {
  if (!(this.cli.has('post') && this.cli.has('username') && this.cli.has('password'))) {
    casper.die("You need to specify a post!", 1);
  }

  this.click("#header-bottom-right > span > a");
});

casper.then(function() {
  this.fill('form#login_login', {
    'user': this.cli.get('username'),
    'passwd': this.cli.get('password')
  }, true);
});

casper.then(function() {
  this.wait(3000)
});

casper.then(function() {
  this.echo(this.getTitle());
  
  var links = this.evaluate(function() {
    return document.querySelectorAll('.thing.link');
  });

  for (var a = 0; a < links.length; a++) {
    var text = links[a].getElementsByTagName('a')[0].textContent
    if (text == self.cli.get('post')) {
      self.log('Match found!', 'info');
    }
  }
});

casper.run();
