package com.artence.cmms.domain.usecase.machine;

import com.artence.cmms.data.repository.MachineRepository;
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
public final class RefreshMachinesUseCase_Factory implements Factory<RefreshMachinesUseCase> {
  private final Provider<MachineRepository> machineRepositoryProvider;

  public RefreshMachinesUseCase_Factory(Provider<MachineRepository> machineRepositoryProvider) {
    this.machineRepositoryProvider = machineRepositoryProvider;
  }

  @Override
  public RefreshMachinesUseCase get() {
    return newInstance(machineRepositoryProvider.get());
  }

  public static RefreshMachinesUseCase_Factory create(
      Provider<MachineRepository> machineRepositoryProvider) {
    return new RefreshMachinesUseCase_Factory(machineRepositoryProvider);
  }

  public static RefreshMachinesUseCase newInstance(MachineRepository machineRepository) {
    return new RefreshMachinesUseCase(machineRepository);
  }
}
