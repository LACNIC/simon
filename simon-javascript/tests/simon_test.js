describe("exists", function() {
	expect(typeof SIMON).not.toBe("undefined");
	console.log("Es travis?")
	console.log(process.env.TRAVIS);
	console.log(process.env.BS_USERNAME);
});
