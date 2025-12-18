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
public final class GetMachineByIdUseCase_Factory implements Factory<GetMachineByIdUseCase> {
  private final Provider<MachineRepository> machineRepositoryProvider;

  public GetMachineByIdUseCase_Factory(Provider<MachineRepository> machineRepositoryProvider) {
    this.machineRepositoryProvider = machineRepositoryProvider;
  }

  @Override
  public GetMachineByIdUseCase get() {
    return newInstance(machineRepositoryProvider.get());
  }

  public static GetMachineByIdUseCase_Factory create(
      Provider<MachineRepository> machineRepositoryProvider) {
    return new GetMachineByIdUseCase_Factory(machineRepositoryProvider);
  }

  public static GetMachineByIdUseCase newInstance(MachineRepository machineRepository) {
    return new GetMachineByIdUseCase(machineRepository);
  }
}
