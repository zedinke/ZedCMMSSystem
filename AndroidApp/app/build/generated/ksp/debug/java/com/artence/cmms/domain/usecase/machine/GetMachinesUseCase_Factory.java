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
public final class GetMachinesUseCase_Factory implements Factory<GetMachinesUseCase> {
  private final Provider<MachineRepository> machineRepositoryProvider;

  public GetMachinesUseCase_Factory(Provider<MachineRepository> machineRepositoryProvider) {
    this.machineRepositoryProvider = machineRepositoryProvider;
  }

  @Override
  public GetMachinesUseCase get() {
    return newInstance(machineRepositoryProvider.get());
  }

  public static GetMachinesUseCase_Factory create(
      Provider<MachineRepository> machineRepositoryProvider) {
    return new GetMachinesUseCase_Factory(machineRepositoryProvider);
  }

  public static GetMachinesUseCase newInstance(MachineRepository machineRepository) {
    return new GetMachinesUseCase(machineRepository);
  }
}
