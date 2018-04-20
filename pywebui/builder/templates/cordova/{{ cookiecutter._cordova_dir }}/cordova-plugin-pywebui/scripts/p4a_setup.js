module.exports = function(context) {
    const process = require('process')
    const child_process = require('child_process')
    const fs = require('fs')
    const pluginDir = context.opts.plugin.dir
    if (fs.existsSync(`${pluginDir}/p4a/dist`)) {
        console.log('python-for-android distribution already built. Reinstall the plugin *and* android platform if you wish to rebuild it.')
    }
    else {
        ['armeabi-v7a', 'x86'].forEach(arch => {
            const distName = `pywebui-${arch}`
            console.log(`Building python-for-android distribution for ${arch}...`)
            child_process.execSync('python-for-android delete_dist pywebui >/dev/null 2>&1 || exit 0', {shell: '/bin/bash'})
            child_process.execSync(`python-for-android apk --dist-name ${distName} --arch ${arch}`, {shell: '/bin/bash', cwd: `${pluginDir}/p4a`})
            child_process.execSync(`python-for-android export_dist --dist-name ${distName} --arch ${arch} dist_${arch}`, {shell: '/bin/bash', cwd: `${pluginDir}/p4a`})
        });
    }
}