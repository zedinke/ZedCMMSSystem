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
public final class GetInventoryUseCase_Factory implements Factory<GetInventoryUseCase> {
  private final Provider<InventoryRepository> inventoryRepositoryProvider;

  public GetInventoryUseCase_Factory(Provider<InventoryRepository> inventoryRepositoryProvider) {
    this.inventoryRepositoryProvider = inventoryRepositoryProvider;
  }

  @Override
  public GetInventoryUseCase get() {
    return newInstance(inventoryRepositoryProvider.get());
  }

  public static GetInventoryUseCase_Factory create(
      Provider<InventoryRepository> inventoryRepositoryProvider) {
    return new GetInventoryUseCase_Factory(inventoryRepositoryProvider);
  }

  public static GetInventoryUseCase newInstance(InventoryRepository inventoryRepository) {
    return new GetInventoryUseCase(inventoryRepository);
  }
}
