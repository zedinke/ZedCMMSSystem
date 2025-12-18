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
public final class GetAssetsUseCase_Factory implements Factory<GetAssetsUseCase> {
  private final Provider<AssetRepository> assetRepositoryProvider;

  public GetAssetsUseCase_Factory(Provider<AssetRepository> assetRepositoryProvider) {
    this.assetRepositoryProvider = assetRepositoryProvider;
  }

  @Override
  public GetAssetsUseCase get() {
    return newInstance(assetRepositoryProvider.get());
  }

  public static GetAssetsUseCase_Factory create(Provider<AssetRepository> assetRepositoryProvider) {
    return new GetAssetsUseCase_Factory(assetRepositoryProvider);
  }

  public static GetAssetsUseCase newInstance(AssetRepository assetRepository) {
    return new GetAssetsUseCase(assetRepository);
  }
}
