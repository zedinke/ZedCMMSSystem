package com.artence.cmms.ui.screens.machines;

import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.QualifierMetadata;
import dagger.internal.ScopeMetadata;
import javax.annotation.processing.Generated;

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
public final class MachinesViewModel_Factory implements Factory<MachinesViewModel> {
  @Override
  public MachinesViewModel get() {
    return newInstance();
  }

  public static MachinesViewModel_Factory create() {
    return InstanceHolder.INSTANCE;
  }

  public static MachinesViewModel newInstance() {
    return new MachinesViewModel();
  }

  private static final class InstanceHolder {
    private static final MachinesViewModel_Factory INSTANCE = new MachinesViewModel_Factory();
  }
}
