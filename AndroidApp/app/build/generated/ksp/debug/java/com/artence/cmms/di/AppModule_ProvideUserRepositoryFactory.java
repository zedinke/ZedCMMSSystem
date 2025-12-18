package com.artence.cmms.di;

import com.artence.cmms.data.local.database.dao.UserDao;
import com.artence.cmms.data.remote.api.UserApi;
import com.artence.cmms.data.repository.UserRepository;
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
public final class AppModule_ProvideUserRepositoryFactory implements Factory<UserRepository> {
  private final Provider<UserDao> userDaoProvider;

  private final Provider<UserApi> userApiProvider;

  public AppModule_ProvideUserRepositoryFactory(Provider<UserDao> userDaoProvider,
      Provider<UserApi> userApiProvider) {
    this.userDaoProvider = userDaoProvider;
    this.userApiProvider = userApiProvider;
  }

  @Override
  public UserRepository get() {
    return provideUserRepository(userDaoProvider.get(), userApiProvider.get());
  }

  public static AppModule_ProvideUserRepositoryFactory create(Provider<UserDao> userDaoProvider,
      Provider<UserApi> userApiProvider) {
    return new AppModule_ProvideUserRepositoryFactory(userDaoProvider, userApiProvider);
  }

  public static UserRepository provideUserRepository(UserDao userDao, UserApi userApi) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.provideUserRepository(userDao, userApi));
  }
}
