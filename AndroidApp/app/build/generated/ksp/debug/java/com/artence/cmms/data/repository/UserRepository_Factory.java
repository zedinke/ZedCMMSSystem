package com.artence.cmms.data.repository;

import com.artence.cmms.data.local.database.dao.UserDao;
import com.artence.cmms.data.remote.api.UserApi;
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
public final class UserRepository_Factory implements Factory<UserRepository> {
  private final Provider<UserDao> userDaoProvider;

  private final Provider<UserApi> userApiProvider;

  public UserRepository_Factory(Provider<UserDao> userDaoProvider,
      Provider<UserApi> userApiProvider) {
    this.userDaoProvider = userDaoProvider;
    this.userApiProvider = userApiProvider;
  }

  @Override
  public UserRepository get() {
    return newInstance(userDaoProvider.get(), userApiProvider.get());
  }

  public static UserRepository_Factory create(Provider<UserDao> userDaoProvider,
      Provider<UserApi> userApiProvider) {
    return new UserRepository_Factory(userDaoProvider, userApiProvider);
  }

  public static UserRepository newInstance(UserDao userDao, UserApi userApi) {
    return new UserRepository(userDao, userApi);
  }
}
