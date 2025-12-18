package com.artence.cmms.di;

import com.artence.cmms.data.local.database.CMMSDatabase;
import com.artence.cmms.data.local.database.dao.WorksheetDao;
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
public final class AppModule_ProvideWorksheetDaoFactory implements Factory<WorksheetDao> {
  private final Provider<CMMSDatabase> databaseProvider;

  public AppModule_ProvideWorksheetDaoFactory(Provider<CMMSDatabase> databaseProvider) {
    this.databaseProvider = databaseProvider;
  }

  @Override
  public WorksheetDao get() {
    return provideWorksheetDao(databaseProvider.get());
  }

  public static AppModule_ProvideWorksheetDaoFactory create(
      Provider<CMMSDatabase> databaseProvider) {
    return new AppModule_ProvideWorksheetDaoFactory(databaseProvider);
  }

  public static WorksheetDao provideWorksheetDao(CMMSDatabase database) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.provideWorksheetDao(database));
  }
}
