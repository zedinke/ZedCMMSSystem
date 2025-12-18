package com.artence.cmms.di;

import com.artence.cmms.data.local.database.dao.PMTaskDao;
import com.artence.cmms.data.remote.api.PMApi;
import com.artence.cmms.data.repository.PMRepository;
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
public final class AppModule_ProvidePMRepositoryFactory implements Factory<PMRepository> {
  private final Provider<PMApi> pmApiProvider;

  private final Provider<PMTaskDao> pmTaskDaoProvider;

  public AppModule_ProvidePMRepositoryFactory(Provider<PMApi> pmApiProvider,
      Provider<PMTaskDao> pmTaskDaoProvider) {
    this.pmApiProvider = pmApiProvider;
    this.pmTaskDaoProvider = pmTaskDaoProvider;
  }

  @Override
  public PMRepository get() {
    return providePMRepository(pmApiProvider.get(), pmTaskDaoProvider.get());
  }

  public static AppModule_ProvidePMRepositoryFactory create(Provider<PMApi> pmApiProvider,
      Provider<PMTaskDao> pmTaskDaoProvider) {
    return new AppModule_ProvidePMRepositoryFactory(pmApiProvider, pmTaskDaoProvider);
  }

  public static PMRepository providePMRepository(PMApi pmApi, PMTaskDao pmTaskDao) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.providePMRepository(pmApi, pmTaskDao));
  }
}
