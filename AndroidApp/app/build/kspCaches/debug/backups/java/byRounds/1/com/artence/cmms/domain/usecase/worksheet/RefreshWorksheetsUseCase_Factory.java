package com.artence.cmms.domain.usecase.worksheet;

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
public final class RefreshWorksheetsUseCase_Factory implements Factory<RefreshWorksheetsUseCase> {
  private final Provider<WorksheetRepository> worksheetRepositoryProvider;

  public RefreshWorksheetsUseCase_Factory(
      Provider<WorksheetRepository> worksheetRepositoryProvider) {
    this.worksheetRepositoryProvider = worksheetRepositoryProvider;
  }

  @Override
  public RefreshWorksheetsUseCase get() {
    return newInstance(worksheetRepositoryProvider.get());
  }

  public static RefreshWorksheetsUseCase_Factory create(
      Provider<WorksheetRepository> worksheetRepositoryProvider) {
    return new RefreshWorksheetsUseCase_Factory(worksheetRepositoryProvider);
  }

  public static RefreshWorksheetsUseCase newInstance(WorksheetRepository worksheetRepository) {
    return new RefreshWorksheetsUseCase(worksheetRepository);
  }
}
