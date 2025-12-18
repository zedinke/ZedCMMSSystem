package com.artence.cmms.data.repository;

import com.artence.cmms.data.local.database.dao.WorksheetDao;
import com.artence.cmms.data.remote.api.WorksheetApi;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
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
public final class WorksheetRepository_Factory implements Factory<WorksheetRepository> {
  private final Provider<WorksheetApi> worksheetApiProvider;

  private final Provider<WorksheetDao> worksheetDaoProvider;

  public WorksheetRepository_Factory(Provider<WorksheetApi> worksheetApiProvider,
      Provider<WorksheetDao> worksheetDaoProvider) {
    this.worksheetApiProvider = worksheetApiProvider;
    this.worksheetDaoProvider = worksheetDaoProvider;
  }

  @Override
  public WorksheetRepository get() {
    return newInstance(worksheetApiProvider.get(), worksheetDaoProvider.get());
  }

  public static WorksheetRepository_Factory create(Provider<WorksheetApi> worksheetApiProvider,
      Provider<WorksheetDao> worksheetDaoProvider) {
    return new WorksheetRepository_Factory(worksheetApiProvider, worksheetDaoProvider);
  }

  public static WorksheetRepository newInstance(WorksheetApi worksheetApi,
      WorksheetDao worksheetDao) {
    return new WorksheetRepository(worksheetApi, worksheetDao);
  }
}
