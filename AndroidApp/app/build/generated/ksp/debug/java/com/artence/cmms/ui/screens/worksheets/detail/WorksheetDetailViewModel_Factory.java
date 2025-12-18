package com.artence.cmms.ui.screens.worksheets.detail;

import com.artence.cmms.data.repository.WorksheetRepository;
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
public final class WorksheetDetailViewModel_Factory implements Factory<WorksheetDetailViewModel> {
  private final Provider<WorksheetRepository> worksheetRepositoryProvider;

  public WorksheetDetailViewModel_Factory(
      Provider<WorksheetRepository> worksheetRepositoryProvider) {
    this.worksheetRepositoryProvider = worksheetRepositoryProvider;
  }

  @Override
  public WorksheetDetailViewModel get() {
    return newInstance(worksheetRepositoryProvider.get());
  }

  public static WorksheetDetailViewModel_Factory create(
      Provider<WorksheetRepository> worksheetRepositoryProvider) {
    return new WorksheetDetailViewModel_Factory(worksheetRepositoryProvider);
  }

  public static WorksheetDetailViewModel newInstance(WorksheetRepository worksheetRepository) {
    return new WorksheetDetailViewModel(worksheetRepository);
  }
}
