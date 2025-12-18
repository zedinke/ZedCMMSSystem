package com.artence.cmms.di;

import com.artence.cmms.data.remote.api.AssetApi;
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
public final class AppModule_ProvideAssetApiFactory implements Factory<AssetApi> {
  private final Provider<Retrofit> retrofitProvider;

  public AppModule_ProvideAssetApiFactory(Provider<Retrofit> retrofitProvider) {
    this.retrofitProvider = retrofitProvider;
  }

  @Override
  public AssetApi get() {
    return provideAssetApi(retrofitProvider.get());
  }

  public static AppModule_ProvideAssetApiFactory create(Provider<Retrofit> retrofitProvider) {
    return new AppModule_ProvideAssetApiFactory(retrofitProvider);
  }

  public static AssetApi provideAssetApi(Retrofit retrofit) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.provideAssetApi(retrofit));
  }
}
