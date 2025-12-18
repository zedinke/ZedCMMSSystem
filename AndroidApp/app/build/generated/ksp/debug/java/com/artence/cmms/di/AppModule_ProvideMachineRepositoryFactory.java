package com.artence.cmms.di;

import com.artence.cmms.data.local.database.dao.MachineDao;
import com.artence.cmms.data.remote.api.MachineApi;
import com.artence.cmms.data.repository.MachineRepository;
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
public final class AppModule_ProvideMachineRepositoryFactory implements Factory<MachineRepository> {
  private final Provider<MachineDao> machineDaoProvider;

  private final Provider<MachineApi> machineApiProvider;

  public AppModule_ProvideMachineRepositoryFactory(Provider<MachineDao> machineDaoProvider,
      Provider<MachineApi> machineApiProvider) {
    this.machineDaoProvider = machineDaoProvider;
    this.machineApiProvider = machineApiProvider;
  }

  @Override
  public MachineRepository get() {
    return provideMachineRepository(machineDaoProvider.get(), machineApiProvider.get());
  }

  public static AppModule_ProvideMachineRepositoryFactory create(
      Provider<MachineDao> machineDaoProvider, Provider<MachineApi> machineApiProvider) {
    return new AppModule_ProvideMachineRepositoryFactory(machineDaoProvider, machineApiProvider);
  }

  public static MachineRepository provideMachineRepository(MachineDao machineDao,
      MachineApi machineApi) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.provideMachineRepository(machineDao, machineApi));
  }
}
