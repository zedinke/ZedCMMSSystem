package com.artence.cmms.ui.screens.assets;

import com.artence.cmms.domain.usecase.asset.GetAssetsUseCase;
import com.artence.cmms.domain.usecase.asset.RefreshAssetsUseCase;
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
public final class AssetsViewModel_Factory implements Factory<AssetsViewModel> {
  private final Provider<GetAssetsUseCase> getAssetsUseCaseProvider;

  private final Provider<RefreshAssetsUseCase> refreshAssetsUseCaseProvider;

  public AssetsViewModel_Factory(Provider<GetAssetsUseCase> getAssetsUseCaseProvider,
      Provider<RefreshAssetsUseCase> refreshAssetsUseCaseProvider) {
    this.getAssetsUseCaseProvider = getAssetsUseCaseProvider;
    this.refreshAssetsUseCaseProvider = refreshAssetsUseCaseProvider;
  }

  @Override
  public AssetsViewModel get() {
    return newInstance(getAssetsUseCaseProvider.get(), refreshAssetsUseCaseProvider.get());
  }

  public static AssetsViewModel_Factory create(Provider<GetAssetsUseCase> getAssetsUseCaseProvider,
      Provider<RefreshAssetsUseCase> refreshAssetsUseCaseProvider) {
    return new AssetsViewModel_Factory(getAssetsUseCaseProvider, refreshAssetsUseCaseProvider);
  }

  public static AssetsViewModel newInstance(GetAssetsUseCase getAssetsUseCase,
      RefreshAssetsUseCase refreshAssetsUseCase) {
    return new AssetsViewModel(getAssetsUseCase, refreshAssetsUseCase);
  }
}
