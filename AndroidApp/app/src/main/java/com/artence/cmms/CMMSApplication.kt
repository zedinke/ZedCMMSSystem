package com.artence.cmms

import android.app.Application
import dagger.hilt.android.HiltAndroidApp

@HiltAndroidApp
class CMMSApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        // Opcionális inicializálások ide
    }
}
