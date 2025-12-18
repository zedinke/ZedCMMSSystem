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
public final class GetInventoryByIdUseCase_Factory implements Factory<GetInventoryByIdUseCase> {
  private final Provider<InventoryRepository> inventoryRepositoryProvider;

  public GetInventoryByIdUseCase_Factory(
      Provider<InventoryRepository> inventoryRepositoryProvider) {
    this.inventoryRepositoryProvider = inventoryRepositoryProvider;
  }

  @Override
  public GetInventoryByIdUseCase get() {
    return newInstance(inventoryRepositoryProvider.get());
  }

  public static GetInventoryByIdUseCase_Factory create(
      Provider<InventoryRepository> inventoryRepositoryProvider) {
    return new GetInventoryByIdUseCase_Factory(inventoryRepositoryProvider);
  }

  public static GetInventoryByIdUseCase newInstance(InventoryRepository inventoryRepository) {
    return new GetInventoryByIdUseCase(inventoryRepository);
  }
}
