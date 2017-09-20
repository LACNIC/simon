describe("Definition test suite", function() {

	it("Is defined", function () {
		define('Simon dep.', ['simon'], function(SIMON) {
				expect(SIMON).toBeDefined();
		});
	});

	it("Behaves like a msms script", function () {
		define('Simon dep.', ['simon'], function(SIMON) {
				expect(foo).toBe(_var);
		});
	});

});
