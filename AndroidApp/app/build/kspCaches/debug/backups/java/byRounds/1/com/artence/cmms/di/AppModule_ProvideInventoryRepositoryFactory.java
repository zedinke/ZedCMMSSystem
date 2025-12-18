package com.artence.cmms.di;

import com.artence.cmms.data.local.database.dao.InventoryDao;
import com.artence.cmms.data.remote.api.InventoryApi;
import com.artence.cmms.data.repository.InventoryRepository;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.Preconditions;
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
public final class AppModule_ProvideInventoryRepositoryFactory implements Factory<InventoryRepository> {
  private final Provider<InventoryApi> inventoryApiProvider;

  private final Provider<InventoryDao> inventoryDaoProvider;

  public AppModule_ProvideInventoryRepositoryFactory(Provider<InventoryApi> inventoryApiProvider,
      Provider<InventoryDao> inventoryDaoProvider) {
    this.inventoryApiProvider = inventoryApiProvider;
    this.inventoryDaoProvider = inventoryDaoProvider;
  }

  @Override
  public InventoryRepository get() {
    return provideInventoryRepository(inventoryApiProvider.get(), inventoryDaoProvider.get());
  }

  public static AppModule_ProvideInventoryRepositoryFactory create(
      Provider<InventoryApi> inventoryApiProvider, Provider<InventoryDao> inventoryDaoProvider) {
    return new AppModule_ProvideInventoryRepositoryFactory(inventoryApiProvider, inventoryDaoProvider);
  }

  public static InventoryRepository provideInventoryRepository(InventoryApi inventoryApi,
      InventoryDao inventoryDao) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.provideInventoryRepository(inventoryApi, inventoryDao));
  }
}
