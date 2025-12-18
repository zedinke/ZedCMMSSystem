package com.artence.cmms.di;

import com.artence.cmms.data.remote.api.WorksheetApi;
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
public final class AppModule_ProvideWorksheetApiFactory implements Factory<WorksheetApi> {
  private final Provider<Retrofit> retrofitProvider;

  public AppModule_ProvideWorksheetApiFactory(Provider<Retrofit> retrofitProvider) {
    this.retrofitProvider = retrofitProvider;
  }

  @Override
  public WorksheetApi get() {
    return provideWorksheetApi(retrofitProvider.get());
  }

  public static AppModule_ProvideWorksheetApiFactory create(Provider<Retrofit> retrofitProvider) {
    return new AppModule_ProvideWorksheetApiFactory(retrofitProvider);
  }

  public static WorksheetApi provideWorksheetApi(Retrofit retrofit) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.provideWorksheetApi(retrofit));
  }
}
