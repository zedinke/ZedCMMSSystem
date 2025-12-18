package com.artence.cmms.ui.screens.worksheets.create;

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
public final class CreateWorksheetViewModel_Factory implements Factory<CreateWorksheetViewModel> {
  private final Provider<WorksheetRepository> worksheetRepositoryProvider;

  public CreateWorksheetViewModel_Factory(
      Provider<WorksheetRepository> worksheetRepositoryProvider) {
    this.worksheetRepositoryProvider = worksheetRepositoryProvider;
  }

  @Override
  public CreateWorksheetViewModel get() {
    return newInstance(worksheetRepositoryProvider.get());
  }

  public static CreateWorksheetViewModel_Factory create(
      Provider<WorksheetRepository> worksheetRepositoryProvider) {
    return new CreateWorksheetViewModel_Factory(worksheetRepositoryProvider);
  }

  public static CreateWorksheetViewModel newInstance(WorksheetRepository worksheetRepository) {
    return new CreateWorksheetViewModel(worksheetRepository);
  }
}
