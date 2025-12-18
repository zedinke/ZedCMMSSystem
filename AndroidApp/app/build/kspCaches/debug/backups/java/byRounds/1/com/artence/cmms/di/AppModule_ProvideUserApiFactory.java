package com.artence.cmms.di;

import com.artence.cmms.data.remote.api.UserApi;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.Preconditions;
import dagger.internal.QualifierMetadata;
import dagger.internal.ScopeMetadata;
import javax.annotation.processing.Generated;
import javax.inject.Provider;
import retrofit2.Retrofit;

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
public final class AppModule_ProvideUserApiFactory implements Factory<UserApi> {
  private final Provider<Retrofit> retrofitProvider;

  public AppModule_ProvideUserApiFactory(Provider<Retrofit> retrofitProvider) {
    this.retrofitProvider = retrofitProvider;
  }

  @Override
  public UserApi get() {
    return provideUserApi(retrofitProvider.get());
  }

  public static AppModule_ProvideUserApiFactory create(Provider<Retrofit> retrofitProvider) {
    return new AppModule_ProvideUserApiFactory(retrofitProvider);
  }

  public static UserApi provideUserApi(Retrofit retrofit) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.provideUserApi(retrofit));
  }
}
