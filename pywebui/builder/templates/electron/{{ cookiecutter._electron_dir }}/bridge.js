const readline = require('readline');
const electron = require('electron');
const { spawn } = require('child_process')
const fs = require('fs')
const path = require('path')

function start_bridge(app) {
  console.log('starting bridge');
  app.on('quit', () => {
    pybridge.stdin.end();
  })
  let pexPath;
  [
    'app.pex',
    path.join('..', 'app.pex'),
    path.join('..', '..', 'app.pex'),
  ].forEach(relativePath => {
    let candidatePath = path.resolve(__dirname, relativePath)
    if (fs.existsSync(candidatePath)) {
      pexPath = candidatePath
    }
  })
  const pybridge = spawn('python', [pexPath])
  const ipcMain = electron.ipcMain;
  const eventSenders = {};
  readline.createInterface({input: pybridge.stdout}).on('line', line => {
    const response = JSON.parse(line)
    console.log('Response', response)
    const dest = eventSenders[response.id]
    if (typeof(dest) !== 'undefined') {
      dest.send('ipcresponse', response)
    }
  })
  readline.createInterface({input: pybridge.stderr}).on('line', line => {
    console.log(line)
  })
  ipcMain.on('ipcrequest', (event, data) => {
    console.log('Request', data)
    eventSenders[data.id] = event.sender;
    pybridge.stdin.write(`${JSON.stringify(data)}\n`)
  });
}

module.exports = start_bridge;
