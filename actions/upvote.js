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

var dump = require('utils').dump;


function getUrl() {
  var base  = "http://reddit.com/";

  if (casper.cli.has('subreddit')) {
    return base + "r/" + casper.cli.get('subreddit');
  }

  return base;
}

casper.start(getUrl(), function() {
  if (!(this.cli.has('post') && this.cli.has('username') && this.cli.has('password'))) {
    casper.die("You need to specify a username, password and post!", 1);
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
  this.wait(1000)
});

casper.then(function() {
  
  var ret = this.evaluate(function() {
    titles = []
    var links = document.querySelectorAll('.thing.link');
    for (var i = 0; i < links.length; ++i) {
      var item = {};
      item.title = links[i].querySelector('a.title').textContent;
      item.url = links[i].querySelector('a.title').href;
      links[i].querySelector('div.arrow.up').className += ' foo-'+i;
      titles.push(item)
    }
    return titles;
  });

  for (var i = 0; i < ret.length; ++i) {
    var text = ret[i].title;
    this.echo(text);
    if (text == this.cli.get('post')) {
      this.log('Match found!', 'info');
      this.log(ret[i].title);
      this.log(ret[i].url);
      this.mouseEvent('mouseover', 'div.foo-'+i);
      this.wait(1000);
      this.mouseEvent('mousedown', 'div.foo-'+i);
      this.wait(500);
      this.mouseEvent('click', 'div.foo-'+i);
      this.wait(500);
      this.mouseEvent('mouseup', 'div.foo-'+i);
      this.wait(1000);
      this.mouseEvent('mouseout', 'div.foo-'+i);
    }
  }
});

casper.run();
