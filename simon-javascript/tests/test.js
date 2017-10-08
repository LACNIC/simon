define(['jquery', 'simon'], function(jQ, SIMON) {

    /*
      SIMON tests
    */

    describe("Definitions", function() {

      it("Global $ is *not* defined", function() {
        expect($).not.toBeDefined();
      });

      it("jQuery (jQ) is defined", function() {
        expect(jQ).toBeDefined();
      });

      it("SIMON is defined", function() {
        expect(SIMON).toBeDefined();
      });

      it("SIMON has init()", function() {
        expect(SIMON.init).toBeDefined();
      });

    }); // end describe

}); // end define
