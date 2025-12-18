package com.artence.cmms.di;

import com.artence.cmms.data.local.database.CMMSDatabase;
import com.artence.cmms.data.local.database.dao.PMTaskDao;
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
public final class AppModule_ProvidePMTaskDaoFactory implements Factory<PMTaskDao> {
  private final Provider<CMMSDatabase> databaseProvider;

  public AppModule_ProvidePMTaskDaoFactory(Provider<CMMSDatabase> databaseProvider) {
    this.databaseProvider = databaseProvider;
  }

  @Override
  public PMTaskDao get() {
    return providePMTaskDao(databaseProvider.get());
  }

  public static AppModule_ProvidePMTaskDaoFactory create(Provider<CMMSDatabase> databaseProvider) {
    return new AppModule_ProvidePMTaskDaoFactory(databaseProvider);
  }

  public static PMTaskDao providePMTaskDao(CMMSDatabase database) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.providePMTaskDao(database));
  }
}
