package com.artence.cmms.di;

import com.artence.cmms.data.local.database.dao.AssetDao;
import com.artence.cmms.data.remote.api.AssetApi;
import com.artence.cmms.data.repository.AssetRepository;
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
public final class AppModule_ProvideAssetRepositoryFactory implements Factory<AssetRepository> {
  private final Provider<AssetApi> assetApiProvider;

  private final Provider<AssetDao> assetDaoProvider;

  public AppModule_ProvideAssetRepositoryFactory(Provider<AssetApi> assetApiProvider,
      Provider<AssetDao> assetDaoProvider) {
    this.assetApiProvider = assetApiProvider;
    this.assetDaoProvider = assetDaoProvider;
  }

  @Override
  public AssetRepository get() {
    return provideAssetRepository(assetApiProvider.get(), assetDaoProvider.get());
  }

  public static AppModule_ProvideAssetRepositoryFactory create(Provider<AssetApi> assetApiProvider,
      Provider<AssetDao> assetDaoProvider) {
    return new AppModule_ProvideAssetRepositoryFactory(assetApiProvider, assetDaoProvider);
  }

  public static AssetRepository provideAssetRepository(AssetApi assetApi, AssetDao assetDao) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.provideAssetRepository(assetApi, assetDao));
  }
}
