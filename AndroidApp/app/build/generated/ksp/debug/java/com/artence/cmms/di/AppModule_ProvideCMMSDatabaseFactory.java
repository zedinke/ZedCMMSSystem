package com.artence.cmms.di;

import android.app.Application;
import com.artence.cmms.data.local.database.CMMSDatabase;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.Preconditions;
import dagger.internal.QualifierMetadata;
import dagger.internal.ScopeMetadata;
import javax.annotation.processing.Generated;
import javax.inject.Provider;

@ScopeMetadata("javax.inject.Singleton")
@QualifierMetadata
@DaggerGenerated
@Generated(
    value = "dagger.internal.codegen.ComponentProcessor",
    comments = "https://dagger.dev"
)
@SuppressWarnings({
    "unchecked",
    "rawtypes",
    "KotlinInternal",
    "KotlinInternalInJava"
})
public final class AppModule_ProvideCMMSDatabaseFactory implements Factory<CMMSDatabase> {
  private final Provider<Application> appProvider;

  public AppModule_ProvideCMMSDatabaseFactory(Provider<Application> appProvider) {
    this.appProvider = appProvider;
  }

  @Override
  public CMMSDatabase get() {
    return provideCMMSDatabase(appProvider.get());
  }

  public static AppModule_ProvideCMMSDatabaseFactory create(Provider<Application> appProvider) {
    return new AppModule_ProvideCMMSDatabaseFactory(appProvider);
  }

  public static CMMSDatabase provideCMMSDatabase(Application app) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.provideCMMSDatabase(app));
  }
}
