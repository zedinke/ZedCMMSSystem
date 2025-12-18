package com.artence.cmms.domain.usecase.auth;

import com.artence.cmms.data.local.datastore.TokenManager;
import com.artence.cmms.data.repository.AuthRepository;
import dagger.internal.DaggerGenerated;
import dagger.internal.Factory;
import dagger.internal.QualifierMetadata;
import dagger.internal.ScopeMetadata;
import javax.annotation.processing.Generated;
import javax.inject.Provider;

@ScopeMetadata
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
public final class LogoutUseCase_Factory implements Factory<LogoutUseCase> {
  private final Provider<AuthRepository> authRepositoryProvider;

  private final Provider<TokenManager> tokenManagerProvider;

  public LogoutUseCase_Factory(Provider<AuthRepository> authRepositoryProvider,
      Provider<TokenManager> tokenManagerProvider) {
    this.authRepositoryProvider = authRepositoryProvider;
    this.tokenManagerProvider = tokenManagerProvider;
  }

  @Override
  public LogoutUseCase get() {
    return newInstance(authRepositoryProvider.get(), tokenManagerProvider.get());
  }

  public static LogoutUseCase_Factory create(Provider<AuthRepository> authRepositoryProvider,
      Provider<TokenManager> tokenManagerProvider) {
    return new LogoutUseCase_Factory(authRepositoryProvider, tokenManagerProvider);
  }

  public static LogoutUseCase newInstance(AuthRepository authRepository,
      TokenManager tokenManager) {
    return new LogoutUseCase(authRepository, tokenManager);
  }
}
