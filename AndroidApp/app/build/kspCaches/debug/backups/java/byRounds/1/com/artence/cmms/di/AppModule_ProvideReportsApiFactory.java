package com.artence.cmms.di;

import com.artence.cmms.data.remote.api.ReportsApi;
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
public final class AppModule_ProvideReportsApiFactory implements Factory<ReportsApi> {
  private final Provider<Retrofit> retrofitProvider;

  public AppModule_ProvideReportsApiFactory(Provider<Retrofit> retrofitProvider) {
    this.retrofitProvider = retrofitProvider;
  }

  @Override
  public ReportsApi get() {
    return provideReportsApi(retrofitProvider.get());
  }

  public static AppModule_ProvideReportsApiFactory create(Provider<Retrofit> retrofitProvider) {
    return new AppModule_ProvideReportsApiFactory(retrofitProvider);
  }

  public static ReportsApi provideReportsApi(Retrofit retrofit) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.provideReportsApi(retrofit));
  }
}
