const process = require('node:process');

const ELK = require('elkjs')
const elk = new ELK()

const args = process.argv.slice(2);
let json = JSON.parse(args[0])

function process_layout(json) {
  console.log(JSON.stringify(json));
}

elk.layout(json).then(process_layout).catch(console.log);

