package com.artence.cmms.data.repository;

import com.artence.cmms.data.local.database.dao.InventoryDao;
import com.artence.cmms.data.remote.api.InventoryApi;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.QualifierMetadata;
import dagger.internal.ScopeMetadata;
import javax.annotation.processing.Generated;
import javax.inject.Provider;

@ScopeMetadata("javax.inject.Singleton")
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
public final class InventoryRepository_Factory implements Factory<InventoryRepository> {
  private final Provider<InventoryDao> inventoryDaoProvider;

  private final Provider<InventoryApi> inventoryApiProvider;

  public InventoryRepository_Factory(Provider<InventoryDao> inventoryDaoProvider,
      Provider<InventoryApi> inventoryApiProvider) {
    this.inventoryDaoProvider = inventoryDaoProvider;
    this.inventoryApiProvider = inventoryApiProvider;
  }

  @Override
  public InventoryRepository get() {
    return newInstance(inventoryDaoProvider.get(), inventoryApiProvider.get());
  }

  public static InventoryRepository_Factory create(Provider<InventoryDao> inventoryDaoProvider,
      Provider<InventoryApi> inventoryApiProvider) {
    return new InventoryRepository_Factory(inventoryDaoProvider, inventoryApiProvider);
  }

  public static InventoryRepository newInstance(InventoryDao inventoryDao,
      InventoryApi inventoryApi) {
    return new InventoryRepository(inventoryDao, inventoryApi);
  }
}
