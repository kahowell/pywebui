# PyWebUI

PyWebUI is a framework to create user interfaces for Python applications using
web technologies such as HTML and CSS.

Right now, the framework is a work-in-progress, and supports Android and
Desktop, using Apache Cordova, python-for-android, and Electron.

## Prerequisites

* NPM
* python-for-android (if building for Android)
* Cordova (if building for Android)

## Quickstart

```bash
pip install pywebui
pywebui create
cd app
pywebui build
```

Running `pywebui create` emits the necessary boilerplate. The resulting
directory has the following structure:

```
.
├── cordova
├── electron
├── flask
├── node_modules
├── package.json
├── package-lock.json
├── src
└── webpack.config.js
```

The root folder contains the common HTML and JavaScript. (A developer should
edit files in `src` as necessary to build the UI).

Each of the `cordova`, `electron`, `flask` folders contains a different strategy
for bootstrapping the UI.

The Cordova bootstrap is used for Mobile versions of the application, while
the Electron bootstrap is used for Desktop versions. The Flask version is not
practical and has security implications and should only be used for development
(if at all).

(More documentation to come)
