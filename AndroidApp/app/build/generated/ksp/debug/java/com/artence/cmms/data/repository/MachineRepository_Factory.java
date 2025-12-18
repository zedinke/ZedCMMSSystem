package com.artence.cmms.data.repository;

import com.artence.cmms.data.local.database.dao.MachineDao;
import com.artence.cmms.data.remote.api.MachineApi;
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
public final class MachineRepository_Factory implements Factory<MachineRepository> {
  private final Provider<MachineDao> machineDaoProvider;

  private final Provider<MachineApi> machineApiProvider;

  public MachineRepository_Factory(Provider<MachineDao> machineDaoProvider,
      Provider<MachineApi> machineApiProvider) {
    this.machineDaoProvider = machineDaoProvider;
    this.machineApiProvider = machineApiProvider;
  }

  @Override
  public MachineRepository get() {
    return newInstance(machineDaoProvider.get(), machineApiProvider.get());
  }

  public static MachineRepository_Factory create(Provider<MachineDao> machineDaoProvider,
      Provider<MachineApi> machineApiProvider) {
    return new MachineRepository_Factory(machineDaoProvider, machineApiProvider);
  }

  public static MachineRepository newInstance(MachineDao machineDao, MachineApi machineApi) {
    return new MachineRepository(machineDao, machineApi);
  }
}
