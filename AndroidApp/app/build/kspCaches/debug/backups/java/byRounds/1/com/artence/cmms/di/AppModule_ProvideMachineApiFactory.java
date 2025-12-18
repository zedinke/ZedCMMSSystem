package com.artence.cmms.di;

import com.artence.cmms.data.remote.api.MachineApi;
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
public final class AppModule_ProvideMachineApiFactory implements Factory<MachineApi> {
  private final Provider<Retrofit> retrofitProvider;

  public AppModule_ProvideMachineApiFactory(Provider<Retrofit> retrofitProvider) {
    this.retrofitProvider = retrofitProvider;
  }

  @Override
  public MachineApi get() {
    return provideMachineApi(retrofitProvider.get());
  }

  public static AppModule_ProvideMachineApiFactory create(Provider<Retrofit> retrofitProvider) {
    return new AppModule_ProvideMachineApiFactory(retrofitProvider);
  }

  public static MachineApi provideMachineApi(Retrofit retrofit) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.provideMachineApi(retrofit));
  }
}
