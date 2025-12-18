package com.artence.cmms.ui.screens.reports;

import com.artence.cmms.data.repository.ReportsRepository;
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
public final class ReportsViewModel_Factory implements Factory<ReportsViewModel> {
  private final Provider<ReportsRepository> reportsRepositoryProvider;

  public ReportsViewModel_Factory(Provider<ReportsRepository> reportsRepositoryProvider) {
    this.reportsRepositoryProvider = reportsRepositoryProvider;
  }

  @Override
  public ReportsViewModel get() {
    return newInstance(reportsRepositoryProvider.get());
  }

  public static ReportsViewModel_Factory create(
      Provider<ReportsRepository> reportsRepositoryProvider) {
    return new ReportsViewModel_Factory(reportsRepositoryProvider);
  }

  public static ReportsViewModel newInstance(ReportsRepository reportsRepository) {
    return new ReportsViewModel(reportsRepository);
  }
}
