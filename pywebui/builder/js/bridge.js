class ElectronRpcTransport {
  constructor() {
    const {ipcRenderer} = require('electron')

    this.ipcRenderer = ipcRenderer
    this.id = 0
    this.pending = {}

    ipcRenderer.on('ipcresponse', (event, response) => {
      const [resolve, reject] = this.pending[response.id]
        if (response.hasOwnProperty('error')) {
          reject(response.error)
        }
        else {
          resolve(response.result)
        }
    });
  }
  sendRequest(data) {
    data.id = this.id++;
    return new Promise((resolve, reject) => {
      this.pending[data.id] = [resolve, reject]
      this.ipcRenderer.send('ipcrequest', data)
    })
  }
  on_ready(func) {
    func()
  }
}

class RestRpcTransport {
  constructor() {
    this.id = 0
  }

  sendRequest(data) {
    data.id = this.id++;
    return new Promise((resolve, reject) => {
      const request = new XMLHttpRequest()
      request.addEventListener('load', function() {
        const response = JSON.parse(this.responseText)
        if (response.hasOwnProperty('error')) {
          reject(response.error)
        }
        else {
          resolve(response.result)
        }
      })
      request.open('POST', '/pywebui')
      request.send(JSON.stringify(data))
    })
  }
  on_ready(func) {
    func()
  }
}

class CordovaRpcTransport {
  constructor() {
    this.id = 0
  }

  sendRequest(data) {
    data.id = this.id++;
    console.log('doing a cordova RPC call!')
    console.log(window.cordova_pywebui_call)
    return new Promise((resolve, reject) => {
      window.cordova_pywebui_call(data, resolve, reject);
    }).then(responseText => {
      const response = JSON.parse(responseText);
      if (response.hasOwnProperty('error')) {
        throw response.error;
      }
      else {
        return response.result
      }
    })
  }

  on_ready(func) {
    document.addEventListener('deviceready', func, false);
  }
}

class ObjectWrapper {
  constructor(rpc, reference) {
    this.rpc = rpc
    this.reference = reference
  }

  call(method_name, args) {
    const request = {
      "jsonrpc": "2.0",
      "method": `${this.reference}.${method_name}`,
      "params": {},
    }
    if (typeof(args) !== 'undefined') {
      request.params.args = args
    }
    return this.rpc.sendRequest(request).then(result => {
      if (result.hasOwnProperty('type') && result.type === 'pythonobject') {
        return new ObjectWrapper(this.rpc, result.reference)
      }
      else {
        return result
      }
    })
  }

  getattr(attribute_name, force_reference) {
    const request = {
      "jsonrpc": "2.0",
      "method": '__bridge.getattr',
      'params': {
        'args': [this.reference, attribute_name],
	'force_reference': force_reference,
      },
    }
    return this.rpc.sendRequest(request)
  }

  setattr(attribute_name, value) {
    const request = {
      "jsonrpc": "2.0",
      "method": '__bridge.setattr',
      'params': {
        'args': [this.reference, attribute_name, value],
      },
    }
    return this.rpc.sendRequest(request)
  }
}

export default class Bridge {
  constructor(rpcTransport = 'auto') {
    let rpcImpl = {
      'electron': ElectronRpcTransport,
      'rest': RestRpcTransport,
      'cordova': CordovaRpcTransport,
    }[rpcTransport];
    if (rpcTransport === 'auto') {
      const userAgent = navigator.userAgent
      if (userAgent.includes('Electron')) {
        rpcImpl = ElectronRpcTransport
      }
      else if (usingCordova()) {
        rpcImpl = CordovaRpcTransport
      }
      else {
        rpcImpl = RestRpcTransport
      }
    }
    this.rpc = new rpcImpl();
  }

  import_module(name) {
    this.rpc.sendRequest({
      "jsonrpc": "2.0",
      "method": "__bridge.import_module",
      "params": {
        "args": [name],
      },
    })
    return new ObjectWrapper(this.rpc, name);
  }

  register_wrap_function(type, func) {
    this.rpc.sendRequest({
      "jsonrpc": "2.0",
      "method": "__bridge.register_wrap_function",
      "params": {
        "args": [type, func],
      },
    })
  }

  on_ready(func) {
    this.rpc.on_ready(func);
  }
}

function usingCordova() {
  return navigator.userAgent.match(/(Android|iPhone|iPad|iPod)/);
}

if (usingCordova()) {
  window.pywebui_using_cordova = true;
  const scriptTag = document.createElement("script");
  scriptTag.setAttribute("src", "cordova.js");
  document.body.appendChild(scriptTag);
}
