package com.artence.cmms.ui.screens.machines.detail;

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
public final class MachineDetailViewModel_Factory implements Factory<MachineDetailViewModel> {
  private final Provider<MachineRepository> machineRepositoryProvider;

  public MachineDetailViewModel_Factory(Provider<MachineRepository> machineRepositoryProvider) {
    this.machineRepositoryProvider = machineRepositoryProvider;
  }

  @Override
  public MachineDetailViewModel get() {
    return newInstance(machineRepositoryProvider.get());
  }

  public static MachineDetailViewModel_Factory create(
      Provider<MachineRepository> machineRepositoryProvider) {
    return new MachineDetailViewModel_Factory(machineRepositoryProvider);
  }

  public static MachineDetailViewModel newInstance(MachineRepository machineRepository) {
    return new MachineDetailViewModel(machineRepository);
  }
}
