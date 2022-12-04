var SHARED_ARRAY;
var WORKER_ARRAY;

function testInstructionLoop(instruction, repetitions) {
  var {spamFunction, param} = ALL_WASM[instruction]
  for (var count = 0; count < repetitions; count++) {
    spamFunction(...param)
  }
  return count
}

async function initAllWasm(){
  var begin = performance.now()
  for (instruction of ALLOP) {
    let {spam, param} = await getParam(instruction)
    ALL_WASM[instruction] = {spamFunction: spam, param: param}
  }
  var end = performance.now()
  while(Object.keys(ALL_WASM).length < 244) {await sleep(100)}
  console.log(end-begin);
}

async function createWorker(wasmModule, param, repetitions, buffer) {
  var worker = new Worker('./web/wasmWorker.js');
  await worker.postMessage({"wasmModule": wasmModule,
                      "param": param,
                      "repetitions": repetitions,
                      "buffer": buffer});
  return worker;
}

async function instantiateWorkers(instruction, repetitions, coreNumber) {
  workerArray = [];
  var {param} = ALL_WASM[instruction]
  var buffer = new SharedArrayBuffer(8);
  const wasmModule = await fetchWASM(instruction)
  for (var count = 0; count < coreNumber; count++) {
    workerArray.push(await createWorker(wasmModule, param, repetitions, buffer));
  }
  var sharedArray = new Uint32Array(buffer);
  while (sharedArray[0]<coreNumber) {await sleep(100)}
  SHARED_ARRAY = buffer;
  WORKER_ARRAY = workerArray;
  console.log("done")
  return 0;
}


async function testInstructionWorkers(coreNumber) {
  var sharedArray = new Uint32Array(SHARED_ARRAY);
  var start = performance.now()
  sharedArray[0] = 0;
  for (var count  = 0; count < coreNumber; count++) {
    WORKER_ARRAY[count].postMessage({"command": "go", "buffer": SHARED_ARRAY});
  }
  while (Atomics.load(sharedArray, 0) < coreNumber) {await sleep(100)};
  var end  = performance.now()
  console.log(end-start)
}
