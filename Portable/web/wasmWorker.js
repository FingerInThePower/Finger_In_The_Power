var SPAM_FUNCTION, PARAM, REPETITIONS;



self.onmessage = function(evt) {
  if (Object.keys(evt.data).length == 4) {
    var {wasmModule, param, repetitions, buffer} = evt.data;
    let instance = new WebAssembly.Instance(wasmModule);
    SPAM_FUNCTION = instance.exports.spam;
    PARAM = param;
    REPETITIONS = repetitions;
    var sharedArray = new Uint32Array(buffer);
    Atomics.add(sharedArray, 0, 1);
  }
  else if (evt.data['command'] == "go") {
    for (var rep = 0; rep < REPETITIONS; rep++) {
      SPAM_FUNCTION(...PARAM);
    }
    var sharedArray = new Uint32Array(evt.data['buffer']);
    Atomics.add(sharedArray, 0, 1);
  }
}
