const CopyWebpackPlugin = require('copy-webpack-plugin')
const path = require('path')
const fs = require('fs')

const config = {
  entry: ['babel-polyfill', './src/index.js'],
  plugins: [
    new CopyWebpackPlugin([
      { from: 'src/index.html', to: '.' }
    ]),
  ],
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        loader: 'babel-loader',
      },
    ],
  },
}

const cordovaConfig = Object.assign({}, config, {
  externals: {
    electron: 'electron',
  },
  output: {
    path: path.resolve(__dirname, 'cordova/www'),
  }
})

const electronConfig = Object.assign({}, config, {
  target: 'electron-renderer',
  output: {
    path: path.resolve(__dirname, 'electron'),
  }
})

const flaskConfig = Object.assign({}, config, {
  externals: {
    electron: 'electron',
  },
  output: {
    path: path.resolve(__dirname, 'flask'),
  }
})

const configs = []

if (fs.existsSync('cordova')) {
  configs.push(cordovaConfig)
}

if (fs.existsSync('electron')) {
  configs.push(electronConfig)
}

if (fs.existsSync('flask')) {
  configs.push(flaskConfig)
}

module.exports = configs
