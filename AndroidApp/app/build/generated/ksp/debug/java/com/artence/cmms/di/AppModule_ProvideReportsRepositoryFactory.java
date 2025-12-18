package com.artence.cmms.di;

import com.artence.cmms.data.remote.api.ReportsApi;
import com.artence.cmms.data.repository.ReportsRepository;
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
public final class AppModule_ProvideReportsRepositoryFactory implements Factory<ReportsRepository> {
  private final Provider<ReportsApi> reportsApiProvider;

  public AppModule_ProvideReportsRepositoryFactory(Provider<ReportsApi> reportsApiProvider) {
    this.reportsApiProvider = reportsApiProvider;
  }

  @Override
  public ReportsRepository get() {
    return provideReportsRepository(reportsApiProvider.get());
  }

  public static AppModule_ProvideReportsRepositoryFactory create(
      Provider<ReportsApi> reportsApiProvider) {
    return new AppModule_ProvideReportsRepositoryFactory(reportsApiProvider);
  }

  public static ReportsRepository provideReportsRepository(ReportsApi reportsApi) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.provideReportsRepository(reportsApi));
  }
}
