import Bridge from './bridge'

const bridge = new Bridge()
bridge.on_ready(function() {
  const sys = bridge.import_module('sys')
  const uuid = bridge.import_module('uuid')
  bridge.import_module('six')

  bridge.register_wrap_function('uuid.UUID', 'six.text_type')

  console.log(sys.data('version'));
  sys.data('version').then(version => {
    console.log('test')
    console.log('got version!', version)
    document.getElementById('python-version').innerHTML = version;
  })

  uuid.call('uuid4', []).then(value => {
    document.getElementById('uuid').innerHTML = value;
  })
})
