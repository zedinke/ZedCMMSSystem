package com.artence.cmms.ui.screens.assets.detail;

import com.artence.cmms.data.repository.AssetRepository;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.QualifierMetadata;
import dagger.internal.ScopeMetadata;
import javax.annotation.processing.Generated;
import javax.inject.Provider;

@ScopeMetadata
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
public final class AssetDetailViewModel_Factory implements Factory<AssetDetailViewModel> {
  private final Provider<AssetRepository> assetRepositoryProvider;

  public AssetDetailViewModel_Factory(Provider<AssetRepository> assetRepositoryProvider) {
    this.assetRepositoryProvider = assetRepositoryProvider;
  }

  @Override
  public AssetDetailViewModel get() {
    return newInstance(assetRepositoryProvider.get());
  }

  public static AssetDetailViewModel_Factory create(
      Provider<AssetRepository> assetRepositoryProvider) {
    return new AssetDetailViewModel_Factory(assetRepositoryProvider);
  }

  public static AssetDetailViewModel newInstance(AssetRepository assetRepository) {
    return new AssetDetailViewModel(assetRepository);
  }
}
