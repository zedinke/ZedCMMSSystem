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
public final class GetAssetByIdUseCase_Factory implements Factory<GetAssetByIdUseCase> {
  private final Provider<AssetRepository> assetRepositoryProvider;

  public GetAssetByIdUseCase_Factory(Provider<AssetRepository> assetRepositoryProvider) {
    this.assetRepositoryProvider = assetRepositoryProvider;
  }

  @Override
  public GetAssetByIdUseCase get() {
    return newInstance(assetRepositoryProvider.get());
  }

  public static GetAssetByIdUseCase_Factory create(
      Provider<AssetRepository> assetRepositoryProvider) {
    return new GetAssetByIdUseCase_Factory(assetRepositoryProvider);
  }

  public static GetAssetByIdUseCase newInstance(AssetRepository assetRepository) {
    return new GetAssetByIdUseCase(assetRepository);
  }
}
