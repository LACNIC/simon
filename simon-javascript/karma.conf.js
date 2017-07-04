// Karma configuration
// Generated on Tue Jun 14 2016 16:30:20 GMT-0300 (UYT)

module.exports = function (config) {

    // define browsers
    config.customLaunchers = {
        chrome_osx: {
            base: 'BrowserStack',
            browser: 'Chrome',
            browser_version: '52',
            os: 'OS X',
            os_version: 'El Capitan',
            displayName: "Chrome OSX Desktop"
        }
    }

    config.set({

        // base path that will be used to resolve all patterns (eg. files, exclude)
        basePath: '',


        // frameworks to use
        // available frameworks: https://npmjs.org/browse/keyword/karma-adapter
        frameworks: ['jasmine'],


        // list of files / patterns to load in the browser
        files: [
            'https://cdn.dev.lacnic.net/jquery-1.11.1.min.js',
            'simon_probe_plugin.js',
            'https://ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js'
        ],


        // list of files to exclude
        exclude: [],


        // preprocess matching files before serving them to the browser
        // available preprocessors: https://npmjs.org/browse/keyword/karma-preprocessor
        preprocessors: {},


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

        // start these browsers
        // available browser launchers: https://npmjs.org/browse/keyword/karma-launcher
        browsers: [Object.keys(config.customLaunchers)],
    })
}
