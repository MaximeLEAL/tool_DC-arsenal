// package com.lexcorp.lexservice - relance du service au boot du telephone
package com.lexcorp.lexservice;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

public class BootReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context ctx, Intent i) {
        if (Intent.ACTION_BOOT_COMPLETED.equals(i.getAction()))
            ctx.startService(new Intent(ctx, LexService.class));
    }
}
