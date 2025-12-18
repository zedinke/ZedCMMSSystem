package com.artence.cmms.domain.usecase.asset;

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
public final class RefreshAssetsUseCase_Factory implements Factory<RefreshAssetsUseCase> {
  private final Provider<AssetRepository> assetRepositoryProvider;

  public RefreshAssetsUseCase_Factory(Provider<AssetRepository> assetRepositoryProvider) {
    this.assetRepositoryProvider = assetRepositoryProvider;
  }

  @Override
  public RefreshAssetsUseCase get() {
    return newInstance(assetRepositoryProvider.get());
  }

  public static RefreshAssetsUseCase_Factory create(
      Provider<AssetRepository> assetRepositoryProvider) {
    return new RefreshAssetsUseCase_Factory(assetRepositoryProvider);
  }

  public static RefreshAssetsUseCase newInstance(AssetRepository assetRepository) {
    return new RefreshAssetsUseCase(assetRepository);
  }
}
