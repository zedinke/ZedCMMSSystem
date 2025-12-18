package com.artence.cmms.di;

import android.content.Context;
import com.artence.cmms.data.local.datastore.TokenManager;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.Preconditions;
import dagger.internal.QualifierMetadata;
import dagger.internal.ScopeMetadata;
import javax.annotation.processing.Generated;
import javax.inject.Provider;
import okhttp3.OkHttpClient;
import okhttp3.logging.HttpLoggingInterceptor;

@ScopeMetadata("javax.inject.Singleton")
@QualifierMetadata("dagger.hilt.android.qualifiers.ApplicationContext")
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
public final class AppModule_ProvideOkHttpClientFactory implements Factory<OkHttpClient> {
  private final Provider<HttpLoggingInterceptor> loggingInterceptorProvider;

  private final Provider<TokenManager> tokenManagerProvider;

  private final Provider<Context> contextProvider;

  public AppModule_ProvideOkHttpClientFactory(
      Provider<HttpLoggingInterceptor> loggingInterceptorProvider,
      Provider<TokenManager> tokenManagerProvider, Provider<Context> contextProvider) {
    this.loggingInterceptorProvider = loggingInterceptorProvider;
    this.tokenManagerProvider = tokenManagerProvider;
    this.contextProvider = contextProvider;
  }

  @Override
  public OkHttpClient get() {
    return provideOkHttpClient(loggingInterceptorProvider.get(), tokenManagerProvider.get(), contextProvider.get());
  }

  public static AppModule_ProvideOkHttpClientFactory create(
      Provider<HttpLoggingInterceptor> loggingInterceptorProvider,
      Provider<TokenManager> tokenManagerProvider, Provider<Context> contextProvider) {
    return new AppModule_ProvideOkHttpClientFactory(loggingInterceptorProvider, tokenManagerProvider, contextProvider);
  }

  public static OkHttpClient provideOkHttpClient(HttpLoggingInterceptor loggingInterceptor,
      TokenManager tokenManager, Context context) {
    return Preconditions.checkNotNullFromProvides(AppModule.INSTANCE.provideOkHttpClient(loggingInterceptor, tokenManager, context));
  }
}
