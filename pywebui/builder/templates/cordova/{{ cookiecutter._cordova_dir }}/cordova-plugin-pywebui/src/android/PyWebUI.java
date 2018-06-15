package io.pywebui.cordova.plugin;

import android.content.Context;
import android.util.Log;
import android.system.Os;
import android.system.ErrnoException;
import android.system.OsConstants;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.io.FileOutputStream;
import io.pywebui.ServicePywebui;

import java.util.concurrent.SynchronousQueue;

import org.apache.cordova.CordovaPlugin;
import org.apache.cordova.CallbackContext;
import org.apache.cordova.CordovaWebView;
import org.apache.cordova.CordovaInterface;
import org.apache.cordova.PluginResult;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.renpy.android.AssetExtract;

public class PyWebUI extends CordovaPlugin {
    private PrintWriter writer;
    private BufferedReader reader;
    String requestFifoPath;
    String responseFifoPath;

    public void deleteFiles(File target) {
        if (target.isDirectory()) {
            for (File child : target.listFiles()) {
                deleteFiles(child);
            }
        }
        target.delete();
    }

    @Override
    public void initialize(CordovaInterface cordova, CordovaWebView webView) {
        super.initialize(cordova, webView);
        Context context = cordova.getActivity().getApplicationContext();
        String androidDataDir = context.getFilesDir().getAbsolutePath();
        String destination = androidDataDir + "/app";
        requestFifoPath = androidDataDir + "/pywebui.request.fifo";
        responseFifoPath = androidDataDir + "/pywebui.response.fifo";
        try {
            for (String fifoPath : new String[]{requestFifoPath, responseFifoPath}) {
                if (!(new File(fifoPath).exists())) {
                    Os.mkfifo(fifoPath, OsConstants.S_IRWXU);
                }
            }
        } catch (ErrnoException e) {
            throw new RuntimeException(e);
        }
        // } catch (IOException e) {
        //     throw new RuntimeException(e);
        // }
        File destinationFolder = new File(destination);
        if (destinationFolder.exists()) {
            deleteFiles(destinationFolder);
        }
        destinationFolder.mkdir();
        AssetExtract extract = new AssetExtract(cordova.getActivity());
        extract.extractTar("private.mp3", destination);
        ServicePywebui.start(cordova.getActivity(), androidDataDir);
    }

    @Override
    public boolean execute(String action, JSONArray args, CallbackContext callbackContext) throws JSONException {
        try {
            JSONObject request = args.getJSONObject(0);
            try {
                if (writer == null) {
                    writer = new PrintWriter(requestFifoPath);
                    reader = new BufferedReader(new FileReader(responseFifoPath));
                }
                writer.println(request.toString());
                writer.flush();
                Log.i("PyWebUI", "waiting for response now");
                String response = reader.readLine();
                Log.i("PyWebUI", "response!" + response);
                PluginResult result = new PluginResult(PluginResult.Status.OK, response);
                callbackContext.sendPluginResult(result);
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
            return true;
        } catch (JSONException e) {
            return false;
        }
    }
}
