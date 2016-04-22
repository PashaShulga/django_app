// package metadata file for Meteor.js

/* jshint strict:false */
/* global Package:true */

Package.describe({
  name: 'twbs:bootstrap',  // http://atmospherejs.com/twbs/bootstrap
  summary: 'The most popular front-end framework for developing responsive, mobile first projects on the web.',
  version: '3.3.6',
  git: 'https://github.com/twbs/bootstrap.git'
});

Package.onUse(function (api) {
  api.versionsFrom('METEOR@1.0');
  api.use('jquery', 'client');
  var assets = [
    'rd/fonts/glyphicons-halflings-regular.eot',
    'rd/fonts/glyphicons-halflings-regular.svg',
    'rd/fonts/glyphicons-halflings-regular.ttf',
    'rd/fonts/glyphicons-halflings-regular.woff',
    'rd/fonts/glyphicons-halflings-regular.woff2'
  ];
  if (api.addAssets) {
    api.addAssets(assets, 'client');
  } else {
    api.addFiles(assets, 'client', { isAsset: true });
  }
  api.addFiles([
    'rd/css/bootstrap.css',
    'rd/js/bootstrap.js'
  ], 'client');
});
