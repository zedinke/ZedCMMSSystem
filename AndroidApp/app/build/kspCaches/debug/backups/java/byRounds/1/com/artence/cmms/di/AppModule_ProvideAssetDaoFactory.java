package com.artence.cmms.di;

import com.artence.cmms.data.local.database.CMMSDatabase;
import com.artence.cmms.data.local.database.dao.AssetDao;
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
public final class AppModule_ProvideAssetDaoFactory implements Factory<AssetDao> {
  private final Provider<CMMSDatabase> databaseProvider;

  public AppModule_ProvideAssetDaoFactory(Provider<CMMSDatabase> databaseProvider) {
    this.databaseProvider = databaseProvider;
  }

  @Override
  public AssetDao get() {
    return provideAssetDao(databaseProvider.get());
  }

  public static AppModule_ProvideAssetDaoFactory create(Provider<CMMSDatabase> databaseProvider) {
    return new AppModule_ProvideAssetDaoFactory(databaseProvider);
  }

  public static AssetDao provideAssetDao(CMMSDatabase database) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.provideAssetDao(database));
  }
}
