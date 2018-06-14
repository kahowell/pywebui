module.exports = function(context) {
    const child_process = require('child_process')
    const pluginDir = context.opts.plugin.dir
    child_process.execSync(`pywebui build-p4a --p4a-dir ${pluginDir}/p4a`)
}