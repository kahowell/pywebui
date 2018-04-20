const readline = require('readline');
const electron = require('electron');
const { spawn } = require('child_process')

function start_bridge(app) {
  console.log('starting bridge');
  app.on('quit', () => {
    pybridge.stdin.end();
  })
  const pybridge = spawn('python', ['-m', 'pywebui.bridge'])
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
  ipcMain.on('ipcrequest', (event, data) => {
    console.log('Request', data)
    eventSenders[data.id] = event.sender;
    pybridge.stdin.write(`${JSON.stringify(data)}\n`)
  });
}

module.exports = start_bridge;
