package com.artence.cmms.ui.screens.pm;

import com.artence.cmms.data.repository.PMRepository;
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
public final class PMViewModel_Factory implements Factory<PMViewModel> {
  private final Provider<PMRepository> pmRepositoryProvider;

  public PMViewModel_Factory(Provider<PMRepository> pmRepositoryProvider) {
    this.pmRepositoryProvider = pmRepositoryProvider;
  }

  @Override
  public PMViewModel get() {
    return newInstance(pmRepositoryProvider.get());
  }

  public static PMViewModel_Factory create(Provider<PMRepository> pmRepositoryProvider) {
    return new PMViewModel_Factory(pmRepositoryProvider);
  }

  public static PMViewModel newInstance(PMRepository pmRepository) {
    return new PMViewModel(pmRepository);
  }
}
