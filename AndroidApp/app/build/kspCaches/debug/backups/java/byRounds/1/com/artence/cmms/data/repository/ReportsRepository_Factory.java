package com.artence.cmms.data.repository;

import com.artence.cmms.data.remote.api.ReportsApi;
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
public final class ReportsRepository_Factory implements Factory<ReportsRepository> {
  private final Provider<ReportsApi> reportsApiProvider;

  public ReportsRepository_Factory(Provider<ReportsApi> reportsApiProvider) {
    this.reportsApiProvider = reportsApiProvider;
  }

  @Override
  public ReportsRepository get() {
    return newInstance(reportsApiProvider.get());
  }

  public static ReportsRepository_Factory create(Provider<ReportsApi> reportsApiProvider) {
    return new ReportsRepository_Factory(reportsApiProvider);
  }

  public static ReportsRepository newInstance(ReportsApi reportsApi) {
    return new ReportsRepository(reportsApi);
  }
}
