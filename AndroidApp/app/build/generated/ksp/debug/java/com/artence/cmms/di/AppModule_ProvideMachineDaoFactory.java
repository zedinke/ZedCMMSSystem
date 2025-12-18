package com.artence.cmms.di;

import com.artence.cmms.data.local.database.CMMSDatabase;
import com.artence.cmms.data.local.database.dao.MachineDao;
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
public final class AppModule_ProvideMachineDaoFactory implements Factory<MachineDao> {
  private final Provider<CMMSDatabase> databaseProvider;

  public AppModule_ProvideMachineDaoFactory(Provider<CMMSDatabase> databaseProvider) {
    this.databaseProvider = databaseProvider;
  }

  @Override
  public MachineDao get() {
    return provideMachineDao(databaseProvider.get());
  }

  public static AppModule_ProvideMachineDaoFactory create(Provider<CMMSDatabase> databaseProvider) {
    return new AppModule_ProvideMachineDaoFactory(databaseProvider);
  }

  public static MachineDao provideMachineDao(CMMSDatabase database) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.provideMachineDao(database));
  }
}
