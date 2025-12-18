package com.artence.cmms.ui.screens.assets.create;

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
public final class CreateAssetViewModel_Factory implements Factory<CreateAssetViewModel> {
  private final Provider<AssetRepository> assetRepositoryProvider;

  public CreateAssetViewModel_Factory(Provider<AssetRepository> assetRepositoryProvider) {
    this.assetRepositoryProvider = assetRepositoryProvider;
  }

  @Override
  public CreateAssetViewModel get() {
    return newInstance(assetRepositoryProvider.get());
  }

  public static CreateAssetViewModel_Factory create(
      Provider<AssetRepository> assetRepositoryProvider) {
    return new CreateAssetViewModel_Factory(assetRepositoryProvider);
  }

  public static CreateAssetViewModel newInstance(AssetRepository assetRepository) {
    return new CreateAssetViewModel(assetRepository);
  }
}
