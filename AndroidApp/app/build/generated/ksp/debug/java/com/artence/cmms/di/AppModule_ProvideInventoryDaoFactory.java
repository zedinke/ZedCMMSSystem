package com.artence.cmms.di;

import com.artence.cmms.data.local.database.CMMSDatabase;
import com.artence.cmms.data.local.database.dao.InventoryDao;
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
public final class AppModule_ProvideInventoryDaoFactory implements Factory<InventoryDao> {
  private final Provider<CMMSDatabase> databaseProvider;

  public AppModule_ProvideInventoryDaoFactory(Provider<CMMSDatabase> databaseProvider) {
    this.databaseProvider = databaseProvider;
  }

  @Override
  public InventoryDao get() {
    return provideInventoryDao(databaseProvider.get());
  }

  public static AppModule_ProvideInventoryDaoFactory create(
      Provider<CMMSDatabase> databaseProvider) {
    return new AppModule_ProvideInventoryDaoFactory(databaseProvider);
  }

  public static InventoryDao provideInventoryDao(CMMSDatabase database) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.provideInventoryDao(database));
  }
}
