package com.artence.cmms.ui.screens.inventory;

import com.artence.cmms.domain.usecase.inventory.GetInventoryUseCase;
import com.artence.cmms.domain.usecase.inventory.RefreshInventoryUseCase;
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
public final class InventoryViewModel_Factory implements Factory<InventoryViewModel> {
  private final Provider<GetInventoryUseCase> getInventoryUseCaseProvider;

  private final Provider<RefreshInventoryUseCase> refreshInventoryUseCaseProvider;

  public InventoryViewModel_Factory(Provider<GetInventoryUseCase> getInventoryUseCaseProvider,
      Provider<RefreshInventoryUseCase> refreshInventoryUseCaseProvider) {
    this.getInventoryUseCaseProvider = getInventoryUseCaseProvider;
    this.refreshInventoryUseCaseProvider = refreshInventoryUseCaseProvider;
  }

  @Override
  public InventoryViewModel get() {
    return newInstance(getInventoryUseCaseProvider.get(), refreshInventoryUseCaseProvider.get());
  }

  public static InventoryViewModel_Factory create(
      Provider<GetInventoryUseCase> getInventoryUseCaseProvider,
      Provider<RefreshInventoryUseCase> refreshInventoryUseCaseProvider) {
    return new InventoryViewModel_Factory(getInventoryUseCaseProvider, refreshInventoryUseCaseProvider);
  }

  public static InventoryViewModel newInstance(GetInventoryUseCase getInventoryUseCase,
      RefreshInventoryUseCase refreshInventoryUseCase) {
    return new InventoryViewModel(getInventoryUseCase, refreshInventoryUseCase);
  }
}
