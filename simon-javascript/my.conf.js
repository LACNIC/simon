// Karma configuration
// Generated on Tue Jun 14 2016 16:30:20 GMT-0300 (UYT)

module.exports = function(config) {
  config.set({

    // base path that will be used to resolve all patterns (eg. files, exclude)
    basePath: '',


    // frameworks to use
    // available frameworks: https://npmjs.org/browse/keyword/karma-adapter
    frameworks: ['jasmine'],


    // list of files / patterns to load in the browser
    files: [
      'jquery1.8.0.js',
      'simon_probe_plugin.js',
      'https://ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js'
    ],


    // list of files to exclude
    exclude: [
    ],


    // preprocess matching files before serving them to the browser
    // available preprocessors: https://npmjs.org/browse/keyword/karma-preprocessor
    preprocessors: {
    },


    // test results reporter to use
    // possible values: 'dots', 'progress'
    // available reporters: https://npmjs.org/browse/keyword/karma-reporter
    reporters: ['progress'],


    // web server port
    port: 9876,


    // enable / disable colors in the output (reporters and logs)
    colors: true,


    // level of logging
    // possible values: config.LOG_DISABLE || config.LOG_ERROR || config.LOG_WARN || config.LOG_INFO || config.LOG_DEBUG
    logLevel: config.LOG_INFO,


    // enable / disable watching file and executing tests whenever any file changes
    autoWatch: true,


    // start these browsers
    // available browser launchers: https://npmjs.org/browse/keyword/karma-launcher
    browsers: ['Chrome', 'Firefox', 'Safari'],//, 'Opera', 'IE'],


    // Continuous Integration mode
    // if true, Karma captures browsers, runs the tests and exits
    singleRun: false,

    // Concurrency level
    // how many browser should be started simultaneous
    concurrency: Infinity,

    /*
     * global config of your BrowserStack account
     */

    browserStack: {
      username: process.env.BS_USERNAME,
      accessKey: process.env.BS_ACCESS_KEY
    },

    // define browsers
    customLaunchers: {
        bs_chrome_windows10: {
        base: 'BrowserStack',
        browser: 'chrome',
        browser_version: '51',
        os: 'windows',
        os_version: '10'
      },
      bs_safari_mac: {
        base: 'BrowserStack',
        browser: 'safari',
        browser_version: '9.1',
        os: 'OS X',
        os_version: 'El Capitan'
      },
      bs_firefox_mac: {
        base: 'BrowserStack',
        browser: 'firefox',
        browser_version: '46.0',
        os: 'OS X',
        os_version: 'El Capitan'
      },
      bs_iphone6: {
        base: 'BrowserStack',
        device: 'iPhone 6',
        os: 'ios',
        os_version: '8.3'
      }
    },

    browsers: ['bs_safari_mac', 'bs_chrome_windows10', 'bs_firefox_mac', 'bs_iphone6']
  })
}
