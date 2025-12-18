package com.artence.cmms.data.repository;

import com.artence.cmms.data.local.database.dao.PMTaskDao;
import com.artence.cmms.data.remote.api.PMApi;
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
public final class PMRepository_Factory implements Factory<PMRepository> {
  private final Provider<PMApi> pmApiProvider;

  private final Provider<PMTaskDao> pmTaskDaoProvider;

  public PMRepository_Factory(Provider<PMApi> pmApiProvider,
      Provider<PMTaskDao> pmTaskDaoProvider) {
    this.pmApiProvider = pmApiProvider;
    this.pmTaskDaoProvider = pmTaskDaoProvider;
  }

  @Override
  public PMRepository get() {
    return newInstance(pmApiProvider.get(), pmTaskDaoProvider.get());
  }

  public static PMRepository_Factory create(Provider<PMApi> pmApiProvider,
      Provider<PMTaskDao> pmTaskDaoProvider) {
    return new PMRepository_Factory(pmApiProvider, pmTaskDaoProvider);
  }

  public static PMRepository newInstance(PMApi pmApi, PMTaskDao pmTaskDao) {
    return new PMRepository(pmApi, pmTaskDao);
  }
}
