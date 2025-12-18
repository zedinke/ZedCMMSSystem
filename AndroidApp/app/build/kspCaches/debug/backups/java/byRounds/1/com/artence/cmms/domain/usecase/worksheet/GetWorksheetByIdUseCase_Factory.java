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
public final class GetWorksheetByIdUseCase_Factory implements Factory<GetWorksheetByIdUseCase> {
  private final Provider<WorksheetRepository> worksheetRepositoryProvider;

  public GetWorksheetByIdUseCase_Factory(
      Provider<WorksheetRepository> worksheetRepositoryProvider) {
    this.worksheetRepositoryProvider = worksheetRepositoryProvider;
  }

  @Override
  public GetWorksheetByIdUseCase get() {
    return newInstance(worksheetRepositoryProvider.get());
  }

  public static GetWorksheetByIdUseCase_Factory create(
      Provider<WorksheetRepository> worksheetRepositoryProvider) {
    return new GetWorksheetByIdUseCase_Factory(worksheetRepositoryProvider);
  }

  public static GetWorksheetByIdUseCase newInstance(WorksheetRepository worksheetRepository) {
    return new GetWorksheetByIdUseCase(worksheetRepository);
  }
}
