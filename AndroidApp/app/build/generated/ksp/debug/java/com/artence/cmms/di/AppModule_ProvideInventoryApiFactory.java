package com.artence.cmms.di;

import com.artence.cmms.data.remote.api.InventoryApi;
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
public final class AppModule_ProvideInventoryApiFactory implements Factory<InventoryApi> {
  private final Provider<Retrofit> retrofitProvider;

  public AppModule_ProvideInventoryApiFactory(Provider<Retrofit> retrofitProvider) {
    this.retrofitProvider = retrofitProvider;
  }

  @Override
  public InventoryApi get() {
    return provideInventoryApi(retrofitProvider.get());
  }

  public static AppModule_ProvideInventoryApiFactory create(Provider<Retrofit> retrofitProvider) {
    return new AppModule_ProvideInventoryApiFactory(retrofitProvider);
  }

  public static InventoryApi provideInventoryApi(Retrofit retrofit) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.provideInventoryApi(retrofit));
  }
}
