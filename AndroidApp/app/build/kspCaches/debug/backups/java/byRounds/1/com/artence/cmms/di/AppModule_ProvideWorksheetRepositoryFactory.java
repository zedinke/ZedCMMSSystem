package com.artence.cmms.di;

import com.artence.cmms.data.local.database.dao.WorksheetDao;
import com.artence.cmms.data.remote.api.WorksheetApi;
import com.artence.cmms.data.repository.WorksheetRepository;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.Preconditions;
import dagger.internal.QualifierMetadata;
import dagger.internal.ScopeMetadata;
import javax.annotation.processing.Generated;
import javax.inject.Provider;

@ScopeMetadata("javax.inject.Singleton")
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
public final class AppModule_ProvideWorksheetRepositoryFactory implements Factory<WorksheetRepository> {
  private final Provider<WorksheetApi> worksheetApiProvider;

  private final Provider<WorksheetDao> worksheetDaoProvider;

  public AppModule_ProvideWorksheetRepositoryFactory(Provider<WorksheetApi> worksheetApiProvider,
      Provider<WorksheetDao> worksheetDaoProvider) {
    this.worksheetApiProvider = worksheetApiProvider;
    this.worksheetDaoProvider = worksheetDaoProvider;
  }

  @Override
  public WorksheetRepository get() {
    return provideWorksheetRepository(worksheetApiProvider.get(), worksheetDaoProvider.get());
  }

  public static AppModule_ProvideWorksheetRepositoryFactory create(
      Provider<WorksheetApi> worksheetApiProvider, Provider<WorksheetDao> worksheetDaoProvider) {
    return new AppModule_ProvideWorksheetRepositoryFactory(worksheetApiProvider, worksheetDaoProvider);
  }

  public static WorksheetRepository provideWorksheetRepository(WorksheetApi worksheetApi,
      WorksheetDao worksheetDao) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.provideWorksheetRepository(worksheetApi, worksheetDao));
  }
}
