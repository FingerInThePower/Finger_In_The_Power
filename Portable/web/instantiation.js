var ALL_WASM = {}
/**
 * getRandomInt - Creates a random int comprised in [0,max[
 *
 * @param  {Number} max Maximum value
 * @return {Number}     Random integer
 */
function getRandomInt(max) {
  return Math.floor(Math.random() * max);
}



/**
 * getRandomFloat32b - Creates a random float on 32bits
 *
 * @param  {Number} max Maximum value
 * @return {Number}     Random Float
 */
function getRandomFloat32b(max) {
  return (Math.fround(Math.random() * max));
}

/**
 * getRandomFloat - Creates a random float on 64bits
 *
 * @param  {Number} max Maximum value
 * @return {Number}     Random Float
 */
function getRandomFloat64b(max) {
  return Math.random() * max;
}


/**
 * initUnopSpam - Instantiate and export a WebAssembly function that spams a UNOP.
 * This is an async function. Use it with await.
 *
 * @param  {String} instruction The name of the UNOP
 * @return {Function}           Function repeatedly calling the UNOP
 */
async function initUnopSpam(instruction) {
  const wasm = await fetch(`./build/${instruction}_spam.wasm`);
  const {instance} = await WebAssembly.instantiateStreaming(wasm);
  var spam = await instance.exports.spam;
  return spam;
}


/**
 * initPunopSpam - Instantiate and export a WebAssembly function that spams a PUNOP.
 * This is an async function. Use it with await.
 *
 * @param  {Array(String)} instructions Both instruction of the PUNOP
 * @return {Function}           Function repeatedly calling the PUNOP
 */
async function initPunopSpam(instructions) {
  const wasm = fetch(`../build/${instructions[0]}_${instructions[1]}_spam.wasm`);
  const {instance} = await WebAssembly.instantiateStreaming(wasm);
  var spam = await instance.exports.spam;
  return spam;
}


async function getParam(instruction){
  // First, we instantiate the spam function, i.e the function repeatedly
  // calling our instruction
  if ((UNOP.includes(instruction)) || (BINOP.includes(instruction)))  {
    var type = instruction.slice(0,3); // type of the instr, can be i32/64 or f32/64
    var spam = await initUnopSpam(instruction);
  }
  else if (Array.isArray(instruction)) {
    var type = instruction[1].slice(0,3); // here we have two different types
    // we need the input/output of the function.
    var spam = await initPunopSpam(instruction);
  }
  // else if (MEMOP.includes(instruction)) {
  //   var type = instruction.slice(0,3);
  //   var spam = await initMemopSpam(instruction);
  // }
  else if (VOP.includes(instruction)) {
    if (instruction[0]=='v') {
      var numType = "i64";
      var paramCount = "2";
    }
    else {
      var {numType, paramCount} = parseVShape(instruction);
    }
    var spam = await initUnopSpam(instruction);

  }
  var param;

  if (VOP.includes(instruction)) {
    param = []
    switch (numType) { // As we have different types, we instantiate the proper parameter
      case 'i8':
        for (var i = 0; i < Number(paramCount); i++) {
          param.push(getRandomInt(Math.pow(2,7)))
        }
        break;
      case 'i16':
        for (var i = 0; i < Number(paramCount); i++) {
          param.push(getRandomInt(Math.pow(2,15)))
        }
        break;
      case 'i32':
        for (var i = 0; i < Number(paramCount); i++) {
          param.push(getRandomInt(Math.pow(2,31)))
        }
        break;
      case 'i64':
        for (var i = 0; i < Number(paramCount); i++) {
          param.push(getRandomInt(Math.pow(2,63)));
        }
        break;

      case 'f32':
        for (var i = 0; i < Number(paramCount); i++) {
          param.push(getRandomFloat32b(Math.pow(2,31)));
        }
        break;

      case 'f64':
        for (var i = 0; i < Number(paramCount); i++) {
          param.push(getRandomFloat64b(Math.pow(2,63)));
        }
        break;
      default:
        console.log("Invalid type");
    }
  }
  else {
    switch (type) { // As we have different types, we instantiate the proper parameter
      case 'i32':
        param = [getRandomInt(Math.pow(2,31))];
        break;
      case 'i64':
        param = [getRandomInt(Math.pow(2,63))];
        break;

      case 'f32':
        param = [getRandomFloat32b(Math.pow(2,30))];
        break;

      case 'f64':
        param = [getRandomFloat64b(Math.pow(2,30))];
        break;
      default:
        console.log("Invalid type");
    }
  }
  return {spam, param}
}



async function fetchWASM(instructions) {
  if (Array.isArray(instruction)) {
    var resp = await fetch(`../build/${instructions[0]}_${instructions[1]}_spam.wasm`);
  }
  else {
    var resp = await fetch(`./build/${instruction}_spam.wasm`);
  }
  var bin = await resp.arrayBuffer();
	var module = new WebAssembly.Module(bin);
  return module
}
