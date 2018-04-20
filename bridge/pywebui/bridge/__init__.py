from importlib import import_module as _import_module
import six
from json import dumps, loads
from uuid import uuid4

class JSONRPCError(Exception):
    def __init__(self, code, message, data=None):
        self.code = code
        self.message = message
        self.data = data


class Bridge:
    def __init__(self, input, output):
        self._objects = {
            '__bridge': self,
        }
        self._object_references = {
            self: '__bridge',
        }
        self._wrap_functions = {}
        self.input = input
        self.output = output

    def import_module(self, name):
        """Import a module into the bridge."""
        if name not in self._objects:
            module = _import_module(name)
            self._objects[name] = module
            self._object_references[module] = name
        return self._objects[name]

    def register_wrap_function(self, wrap_type, wrap_function):
        if type(wrap_type) is six.text_type:
            wrap_type = self.resolve_reference(wrap_type)
        if type(wrap_function) is six.text_type:
            wrap_function = self.resolve_reference(wrap_function)
        self._wrap_functions[wrap_type] = wrap_function

    def resolve_reference(self, reference):
        if '.' in reference:
            reference, attr_name = reference.rsplit('.', 1)
        else:
            method_name = None

        _object = self._objects.get(reference, None)
        if _object is None:
            raise AttributeError('Reference "{}" not found in bridge'.format(reference))

        if attr_name:
            return getattr(_object, attr_name)
        return _object

    def wrap_object(self, value):
        wrap_function = self._wrap_functions.get(type(value), None)
        if wrap_function:
            return wrap_function(value)

        if value not in self._object_references:
            self._object_references[value] = str(uuid4())
        return {
            'type': 'pythonobject',
            'reference': self._object_references[value],
        }

    def unwrap_object(self, value):
        if value.get('type', None) == 'pythonobject':
            return self._objects[value['reference']]
        return value

    def release(self, value):
        reference = self._object_references[value]
        del self._object_references[value]
        del self._objects[reference]

    def run(self):
        while True:
            line = self.input.readline()
            if line == '':
                return
            self.handle_request(line)

    def handle_request(self, request_json):
        response = {
            'jsonrpc': '2.0',
        }

        try:
            try:
                request = loads(request_json, object_hook=self.unwrap_object)
                version = request['jsonrpc']
            except (ValueError, KeyError) as e:
                raise JSONRPCError(-32700, 'Parse error', data=str(e))

            if version != '2.0':
                raise JSONRPCError(-32603, 'Only JSON-RPC 2.0 supported')

            if type(request) is not dict:
                raise JSONRPCError(-32600, 'Invalid Request')

            request_id = request.get('id', None)
            if request_id is not None:
                response['id'] = request_id

            method = request.get('method', None)
            if method is None:
                raise JSONRPCError(-32600, 'Invalid Request')
            params = request.get('params', [])

            try:
                method = self.resolve_reference(method)
            except (AttributeError, ValueError) as e:
                raise JSONRPCError(-32601, 'Method not found', data=str(e))

            try:
                response['result'] = method(*params)
            except Exception as e:
                raise JSONRPCError(-32000, 'General error', data=str(e))

            try:
                self.output.write(dumps(response, default=self.wrap_object))
                self.output.write('\n')
                self.output.flush()
            except TypeError as e:
                raise JSONRPCError(-32603, 'Error encoding response', data=str(e))

        except JSONRPCError as e:
            if 'result' in response.keys():
                del response['result']
            response['error'] = {
                'code': e.code,
                'message': e.message,
            }
            if e.data is not None:
                response['error']['data'] = e.data
            self.output.write(dumps(response))
            self.output.write('\n')
            self.output.flush()

    def data(self, reference, name):
        obj = self._objects[reference]
        return getattr(obj, name)
