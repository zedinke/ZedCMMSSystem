package com.artence.cmms.domain.usecase.inventory;

import com.artence.cmms.data.repository.InventoryRepository;
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
public final class RefreshInventoryUseCase_Factory implements Factory<RefreshInventoryUseCase> {
  private final Provider<InventoryRepository> inventoryRepositoryProvider;

  public RefreshInventoryUseCase_Factory(
      Provider<InventoryRepository> inventoryRepositoryProvider) {
    this.inventoryRepositoryProvider = inventoryRepositoryProvider;
  }

  @Override
  public RefreshInventoryUseCase get() {
    return newInstance(inventoryRepositoryProvider.get());
  }

  public static RefreshInventoryUseCase_Factory create(
      Provider<InventoryRepository> inventoryRepositoryProvider) {
    return new RefreshInventoryUseCase_Factory(inventoryRepositoryProvider);
  }

  public static RefreshInventoryUseCase newInstance(InventoryRepository inventoryRepository) {
    return new RefreshInventoryUseCase(inventoryRepository);
  }
}
