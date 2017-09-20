require.config({
  // Karma serves files under `/base`,
  // which is the `basePath` from your config file.
  baseUrl: '/base',

  paths: {
      "simon": "simon_probe_plugin"
  },

  // Example of using shim to load non AMD libraries (such as Backbone, jquery).
  shim: {
    // 'legacy-library': {
    //   deps: [],
    //   exports: 'global'
    // }
  },

  // require files under Karma's /base
  deps: [],

  // We have to kickoff testing framework,
  // after RequireJS is done with loading all the files.
  callback: window.__karma__.start
});
