package com.artence.cmms.ui.screens.settings;

import com.artence.cmms.data.local.datastore.TokenManager;
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
public final class SettingsViewModel_Factory implements Factory<SettingsViewModel> {
  private final Provider<TokenManager> tokenManagerProvider;

  public SettingsViewModel_Factory(Provider<TokenManager> tokenManagerProvider) {
    this.tokenManagerProvider = tokenManagerProvider;
  }

  @Override
  public SettingsViewModel get() {
    return newInstance(tokenManagerProvider.get());
  }

  public static SettingsViewModel_Factory create(Provider<TokenManager> tokenManagerProvider) {
    return new SettingsViewModel_Factory(tokenManagerProvider);
  }

  public static SettingsViewModel newInstance(TokenManager tokenManager) {
    return new SettingsViewModel(tokenManager);
  }
}
