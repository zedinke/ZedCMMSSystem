package com.artence.cmms.di;

import com.artence.cmms.data.remote.api.PMApi;
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
public final class AppModule_ProvidePMApiFactory implements Factory<PMApi> {
  private final Provider<Retrofit> retrofitProvider;

  public AppModule_ProvidePMApiFactory(Provider<Retrofit> retrofitProvider) {
    this.retrofitProvider = retrofitProvider;
  }

  @Override
  public PMApi get() {
    return providePMApi(retrofitProvider.get());
  }

  public static AppModule_ProvidePMApiFactory create(Provider<Retrofit> retrofitProvider) {
    return new AppModule_ProvidePMApiFactory(retrofitProvider);
  }

  public static PMApi providePMApi(Retrofit retrofit) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.providePMApi(retrofit));
  }
}
