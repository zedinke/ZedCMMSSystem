package com.artence.cmms.ui.screens.inventory.detail;

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
public final class InventoryDetailViewModel_Factory implements Factory<InventoryDetailViewModel> {
  private final Provider<InventoryRepository> inventoryRepositoryProvider;

  public InventoryDetailViewModel_Factory(
      Provider<InventoryRepository> inventoryRepositoryProvider) {
    this.inventoryRepositoryProvider = inventoryRepositoryProvider;
  }

  @Override
  public InventoryDetailViewModel get() {
    return newInstance(inventoryRepositoryProvider.get());
  }

  public static InventoryDetailViewModel_Factory create(
      Provider<InventoryRepository> inventoryRepositoryProvider) {
    return new InventoryDetailViewModel_Factory(inventoryRepositoryProvider);
  }

  public static InventoryDetailViewModel newInstance(InventoryRepository inventoryRepository) {
    return new InventoryDetailViewModel(inventoryRepository);
  }
}
