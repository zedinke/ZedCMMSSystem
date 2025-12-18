package com.artence.cmms.ui.screens.worksheets;

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
public final class WorksheetsViewModel_Factory implements Factory<WorksheetsViewModel> {
  @Override
  public WorksheetsViewModel get() {
    return newInstance();
  }

  public static WorksheetsViewModel_Factory create() {
    return InstanceHolder.INSTANCE;
  }

  public static WorksheetsViewModel newInstance() {
    return new WorksheetsViewModel();
  }

  private static final class InstanceHolder {
    private static final WorksheetsViewModel_Factory INSTANCE = new WorksheetsViewModel_Factory();
  }
}
