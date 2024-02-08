// Copyright 2020 The Chromium Authors. All rights reserved.
package org.kivy.plugins.messaging;

import android.util.Log;

import java.util.concurrent.atomic.AtomicBoolean;

public class KivyFirebaseMessagingBackgroundExecutor {
private static AtomicBoolean started = new AtomicBoolean(false);
    public static void startBackgroundPythonService() {

        Log.d("BackgroundExecutor", "Starting background service");
        ru.asoms.myapp.ServicePythonnotificationhandler.start(ContextHolder.getApplicationContext(), "");
        Log.d("BackgroundExecutor", "Background service started");

    }

}
