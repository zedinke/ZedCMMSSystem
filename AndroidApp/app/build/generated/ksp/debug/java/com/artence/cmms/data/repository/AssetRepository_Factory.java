package com.artence.cmms.data.repository;

import com.artence.cmms.data.local.database.dao.AssetDao;
import com.artence.cmms.data.remote.api.AssetApi;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
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
public final class AssetRepository_Factory implements Factory<AssetRepository> {
  private final Provider<AssetApi> assetApiProvider;

  private final Provider<AssetDao> assetDaoProvider;

  public AssetRepository_Factory(Provider<AssetApi> assetApiProvider,
      Provider<AssetDao> assetDaoProvider) {
    this.assetApiProvider = assetApiProvider;
    this.assetDaoProvider = assetDaoProvider;
  }

  @Override
  public AssetRepository get() {
    return newInstance(assetApiProvider.get(), assetDaoProvider.get());
  }

  public static AssetRepository_Factory create(Provider<AssetApi> assetApiProvider,
      Provider<AssetDao> assetDaoProvider) {
    return new AssetRepository_Factory(assetApiProvider, assetDaoProvider);
  }

  public static AssetRepository newInstance(AssetApi assetApi, AssetDao assetDao) {
    return new AssetRepository(assetApi, assetDao);
  }
}
