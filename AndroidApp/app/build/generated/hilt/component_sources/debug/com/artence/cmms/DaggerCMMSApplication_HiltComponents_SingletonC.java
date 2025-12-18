package com.artence.cmms;

import android.app.Activity;
import android.app.Service;
import android.view.View;
import androidx.fragment.app.Fragment;
import androidx.lifecycle.SavedStateHandle;
import androidx.lifecycle.ViewModel;
import com.artence.cmms.data.local.database.CMMSDatabase;
import com.artence.cmms.data.local.database.dao.AssetDao;
import com.artence.cmms.data.local.database.dao.InventoryDao;
import com.artence.cmms.data.local.database.dao.MachineDao;
import com.artence.cmms.data.local.database.dao.PMTaskDao;
import com.artence.cmms.data.local.database.dao.WorksheetDao;
import com.artence.cmms.data.local.datastore.TokenManager;
import com.artence.cmms.data.remote.api.AssetApi;
import com.artence.cmms.data.remote.api.AuthApi;
import com.artence.cmms.data.remote.api.InventoryApi;
import com.artence.cmms.data.remote.api.MachineApi;
import com.artence.cmms.data.remote.api.PMApi;
import com.artence.cmms.data.remote.api.ReportsApi;
import com.artence.cmms.data.remote.api.WorksheetApi;
import com.artence.cmms.data.repository.AssetRepository;
import com.artence.cmms.data.repository.AuthRepository;
import com.artence.cmms.data.repository.InventoryRepository;
import com.artence.cmms.data.repository.MachineRepository;
import com.artence.cmms.data.repository.PMRepository;
import com.artence.cmms.data.repository.ReportsRepository;
import com.artence.cmms.data.repository.WorksheetRepository;
import com.artence.cmms.di.AppModule;
import com.artence.cmms.di.AppModule_ProvideAssetApiFactory;
import com.artence.cmms.di.AppModule_ProvideAssetDaoFactory;
import com.artence.cmms.di.AppModule_ProvideAssetRepositoryFactory;
import com.artence.cmms.di.AppModule_ProvideAuthApiFactory;
import com.artence.cmms.di.AppModule_ProvideAuthRepositoryFactory;
import com.artence.cmms.di.AppModule_ProvideCMMSDatabaseFactory;
import com.artence.cmms.di.AppModule_ProvideInventoryApiFactory;
import com.artence.cmms.di.AppModule_ProvideInventoryDaoFactory;
import com.artence.cmms.di.AppModule_ProvideInventoryRepositoryFactory;
import com.artence.cmms.di.AppModule_ProvideLoggingInterceptorFactory;
import com.artence.cmms.di.AppModule_ProvideMachineApiFactory;
import com.artence.cmms.di.AppModule_ProvideMachineDaoFactory;
import com.artence.cmms.di.AppModule_ProvideMachineRepositoryFactory;
import com.artence.cmms.di.AppModule_ProvideOkHttpClientFactory;
import com.artence.cmms.di.AppModule_ProvidePMApiFactory;
import com.artence.cmms.di.AppModule_ProvidePMRepositoryFactory;
import com.artence.cmms.di.AppModule_ProvidePMTaskDaoFactory;
import com.artence.cmms.di.AppModule_ProvideReportsApiFactory;
import com.artence.cmms.di.AppModule_ProvideReportsRepositoryFactory;
import com.artence.cmms.di.AppModule_ProvideRetrofitFactory;
import com.artence.cmms.di.AppModule_ProvideTokenManagerFactory;
import com.artence.cmms.di.AppModule_ProvideWorksheetApiFactory;
import com.artence.cmms.di.AppModule_ProvideWorksheetDaoFactory;
import com.artence.cmms.di.AppModule_ProvideWorksheetRepositoryFactory;
import com.artence.cmms.domain.usecase.asset.GetAssetsUseCase;
import com.artence.cmms.domain.usecase.asset.RefreshAssetsUseCase;
import com.artence.cmms.domain.usecase.auth.LoginUseCase;
import com.artence.cmms.domain.usecase.inventory.GetInventoryUseCase;
import com.artence.cmms.domain.usecase.inventory.RefreshInventoryUseCase;
import com.artence.cmms.ui.screens.assets.AssetsViewModel;
import com.artence.cmms.ui.screens.assets.AssetsViewModel_HiltModules_KeyModule_ProvideFactory;
import com.artence.cmms.ui.screens.assets.create.CreateAssetViewModel;
import com.artence.cmms.ui.screens.assets.create.CreateAssetViewModel_HiltModules_KeyModule_ProvideFactory;
import com.artence.cmms.ui.screens.assets.detail.AssetDetailViewModel;
import com.artence.cmms.ui.screens.assets.detail.AssetDetailViewModel_HiltModules_KeyModule_ProvideFactory;
import com.artence.cmms.ui.screens.dashboard.DashboardViewModel;
import com.artence.cmms.ui.screens.dashboard.DashboardViewModel_HiltModules_KeyModule_ProvideFactory;
import com.artence.cmms.ui.screens.inventory.InventoryViewModel;
import com.artence.cmms.ui.screens.inventory.InventoryViewModel_HiltModules_KeyModule_ProvideFactory;
import com.artence.cmms.ui.screens.inventory.create.CreateInventoryViewModel;
import com.artence.cmms.ui.screens.inventory.create.CreateInventoryViewModel_HiltModules_KeyModule_ProvideFactory;
import com.artence.cmms.ui.screens.inventory.detail.InventoryDetailViewModel;
import com.artence.cmms.ui.screens.inventory.detail.InventoryDetailViewModel_HiltModules_KeyModule_ProvideFactory;
import com.artence.cmms.ui.screens.login.LoginViewModel;
import com.artence.cmms.ui.screens.login.LoginViewModel_HiltModules_KeyModule_ProvideFactory;
import com.artence.cmms.ui.screens.machines.MachinesViewModel;
import com.artence.cmms.ui.screens.machines.MachinesViewModel_HiltModules_KeyModule_ProvideFactory;
import com.artence.cmms.ui.screens.machines.detail.MachineDetailViewModel;
import com.artence.cmms.ui.screens.machines.detail.MachineDetailViewModel_HiltModules_KeyModule_ProvideFactory;
import com.artence.cmms.ui.screens.pm.PMViewModel;
import com.artence.cmms.ui.screens.pm.PMViewModel_HiltModules_KeyModule_ProvideFactory;
import com.artence.cmms.ui.screens.reports.ReportsViewModel;
import com.artence.cmms.ui.screens.reports.ReportsViewModel_HiltModules_KeyModule_ProvideFactory;
import com.artence.cmms.ui.screens.settings.SettingsViewModel;
import com.artence.cmms.ui.screens.settings.SettingsViewModel_HiltModules_KeyModule_ProvideFactory;
import com.artence.cmms.ui.screens.worksheets.WorksheetsViewModel;
import com.artence.cmms.ui.screens.worksheets.WorksheetsViewModel_HiltModules_KeyModule_ProvideFactory;
import com.artence.cmms.ui.screens.worksheets.create.CreateWorksheetViewModel;
import com.artence.cmms.ui.screens.worksheets.create.CreateWorksheetViewModel_HiltModules_KeyModule_ProvideFactory;
import com.artence.cmms.ui.screens.worksheets.detail.WorksheetDetailViewModel;
import com.artence.cmms.ui.screens.worksheets.detail.WorksheetDetailViewModel_HiltModules_KeyModule_ProvideFactory;
import com.google.errorprone.annotations.CanIgnoreReturnValue;
import dagger.hilt.android.ActivityRetainedLifecycle;
import dagger.hilt.android.ViewModelLifecycle;
import dagger.hilt.android.flags.HiltWrapper_FragmentGetContextFix_FragmentGetContextFixModule;
import dagger.hilt.android.internal.builders.ActivityComponentBuilder;
import dagger.hilt.android.internal.builders.ActivityRetainedComponentBuilder;
import dagger.hilt.android.internal.builders.FragmentComponentBuilder;
import dagger.hilt.android.internal.builders.ServiceComponentBuilder;
import dagger.hilt.android.internal.builders.ViewComponentBuilder;
import dagger.hilt.android.internal.builders.ViewModelComponentBuilder;
import dagger.hilt.android.internal.builders.ViewWithFragmentComponentBuilder;
import dagger.hilt.android.internal.lifecycle.DefaultViewModelFactories;
import dagger.hilt.android.internal.lifecycle.DefaultViewModelFactories_InternalFactoryFactory_Factory;
import dagger.hilt.android.internal.managers.ActivityRetainedComponentManager_LifecycleModule_ProvideActivityRetainedLifecycleFactory;
import dagger.hilt.android.internal.managers.SavedStateHandleHolder;
import dagger.hilt.android.internal.modules.ApplicationContextModule;
import dagger.hilt.android.internal.modules.ApplicationContextModule_ProvideApplicationFactory;
import dagger.hilt.android.internal.modules.ApplicationContextModule_ProvideContextFactory;
import dagger.internal.DaggerGenerated;
import dagger.internal.DoubleCheck;
import dagger.internal.MapBuilder;
import dagger.internal.Preconditions;
import dagger.internal.SetBuilder;
import java.util.Collections;
import java.util.Map;
import java.util.Set;
import javax.annotation.processing.Generated;
import javax.inject.Provider;
import okhttp3.OkHttpClient;
import okhttp3.logging.HttpLoggingInterceptor;
import retrofit2.Retrofit;

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
public final class DaggerCMMSApplication_HiltComponents_SingletonC {
  private DaggerCMMSApplication_HiltComponents_SingletonC() {
  }

  public static Builder builder() {
    return new Builder();
  }

  public static final class Builder {
    private ApplicationContextModule applicationContextModule;

    private Builder() {
    }

    /**
     * @deprecated This module is declared, but an instance is not used in the component. This method is a no-op. For more, see https://dagger.dev/unused-modules.
     */
    @Deprecated
    public Builder appModule(AppModule appModule) {
      Preconditions.checkNotNull(appModule);
      return this;
    }

    public Builder applicationContextModule(ApplicationContextModule applicationContextModule) {
      this.applicationContextModule = Preconditions.checkNotNull(applicationContextModule);
      return this;
    }

    /**
     * @deprecated This module is declared, but an instance is not used in the component. This method is a no-op. For more, see https://dagger.dev/unused-modules.
     */
    @Deprecated
    public Builder hiltWrapper_FragmentGetContextFix_FragmentGetContextFixModule(
        HiltWrapper_FragmentGetContextFix_FragmentGetContextFixModule hiltWrapper_FragmentGetContextFix_FragmentGetContextFixModule) {
      Preconditions.checkNotNull(hiltWrapper_FragmentGetContextFix_FragmentGetContextFixModule);
      return this;
    }

    public CMMSApplication_HiltComponents.SingletonC build() {
      Preconditions.checkBuilderRequirement(applicationContextModule, ApplicationContextModule.class);
      return new SingletonCImpl(applicationContextModule);
    }
  }

  private static final class ActivityRetainedCBuilder implements CMMSApplication_HiltComponents.ActivityRetainedC.Builder {
    private final SingletonCImpl singletonCImpl;

    private SavedStateHandleHolder savedStateHandleHolder;

    private ActivityRetainedCBuilder(SingletonCImpl singletonCImpl) {
      this.singletonCImpl = singletonCImpl;
    }

    @Override
    public ActivityRetainedCBuilder savedStateHandleHolder(
        SavedStateHandleHolder savedStateHandleHolder) {
      this.savedStateHandleHolder = Preconditions.checkNotNull(savedStateHandleHolder);
      return this;
    }

    @Override
    public CMMSApplication_HiltComponents.ActivityRetainedC build() {
      Preconditions.checkBuilderRequirement(savedStateHandleHolder, SavedStateHandleHolder.class);
      return new ActivityRetainedCImpl(singletonCImpl, savedStateHandleHolder);
    }
  }

  private static final class ActivityCBuilder implements CMMSApplication_HiltComponents.ActivityC.Builder {
    private final SingletonCImpl singletonCImpl;

    private final ActivityRetainedCImpl activityRetainedCImpl;

    private Activity activity;

    private ActivityCBuilder(SingletonCImpl singletonCImpl,
        ActivityRetainedCImpl activityRetainedCImpl) {
      this.singletonCImpl = singletonCImpl;
      this.activityRetainedCImpl = activityRetainedCImpl;
    }

    @Override
    public ActivityCBuilder activity(Activity activity) {
      this.activity = Preconditions.checkNotNull(activity);
      return this;
    }

    @Override
    public CMMSApplication_HiltComponents.ActivityC build() {
      Preconditions.checkBuilderRequirement(activity, Activity.class);
      return new ActivityCImpl(singletonCImpl, activityRetainedCImpl, activity);
    }
  }

  private static final class FragmentCBuilder implements CMMSApplication_HiltComponents.FragmentC.Builder {
    private final SingletonCImpl singletonCImpl;

    private final ActivityRetainedCImpl activityRetainedCImpl;

    private final ActivityCImpl activityCImpl;

    private Fragment fragment;

    private FragmentCBuilder(SingletonCImpl singletonCImpl,
        ActivityRetainedCImpl activityRetainedCImpl, ActivityCImpl activityCImpl) {
      this.singletonCImpl = singletonCImpl;
      this.activityRetainedCImpl = activityRetainedCImpl;
      this.activityCImpl = activityCImpl;
    }

    @Override
    public FragmentCBuilder fragment(Fragment fragment) {
      this.fragment = Preconditions.checkNotNull(fragment);
      return this;
    }

    @Override
    public CMMSApplication_HiltComponents.FragmentC build() {
      Preconditions.checkBuilderRequirement(fragment, Fragment.class);
      return new FragmentCImpl(singletonCImpl, activityRetainedCImpl, activityCImpl, fragment);
    }
  }

  private static final class ViewWithFragmentCBuilder implements CMMSApplication_HiltComponents.ViewWithFragmentC.Builder {
    private final SingletonCImpl singletonCImpl;

    private final ActivityRetainedCImpl activityRetainedCImpl;

    private final ActivityCImpl activityCImpl;

    private final FragmentCImpl fragmentCImpl;

    private View view;

    private ViewWithFragmentCBuilder(SingletonCImpl singletonCImpl,
        ActivityRetainedCImpl activityRetainedCImpl, ActivityCImpl activityCImpl,
        FragmentCImpl fragmentCImpl) {
      this.singletonCImpl = singletonCImpl;
      this.activityRetainedCImpl = activityRetainedCImpl;
      this.activityCImpl = activityCImpl;
      this.fragmentCImpl = fragmentCImpl;
    }

    @Override
    public ViewWithFragmentCBuilder view(View view) {
      this.view = Preconditions.checkNotNull(view);
      return this;
    }

    @Override
    public CMMSApplication_HiltComponents.ViewWithFragmentC build() {
      Preconditions.checkBuilderRequirement(view, View.class);
      return new ViewWithFragmentCImpl(singletonCImpl, activityRetainedCImpl, activityCImpl, fragmentCImpl, view);
    }
  }

  private static final class ViewCBuilder implements CMMSApplication_HiltComponents.ViewC.Builder {
    private final SingletonCImpl singletonCImpl;

    private final ActivityRetainedCImpl activityRetainedCImpl;

    private final ActivityCImpl activityCImpl;

    private View view;

    private ViewCBuilder(SingletonCImpl singletonCImpl, ActivityRetainedCImpl activityRetainedCImpl,
        ActivityCImpl activityCImpl) {
      this.singletonCImpl = singletonCImpl;
      this.activityRetainedCImpl = activityRetainedCImpl;
      this.activityCImpl = activityCImpl;
    }

    @Override
    public ViewCBuilder view(View view) {
      this.view = Preconditions.checkNotNull(view);
      return this;
    }

    @Override
    public CMMSApplication_HiltComponents.ViewC build() {
      Preconditions.checkBuilderRequirement(view, View.class);
      return new ViewCImpl(singletonCImpl, activityRetainedCImpl, activityCImpl, view);
    }
  }

  private static final class ViewModelCBuilder implements CMMSApplication_HiltComponents.ViewModelC.Builder {
    private final SingletonCImpl singletonCImpl;

    private final ActivityRetainedCImpl activityRetainedCImpl;

    private SavedStateHandle savedStateHandle;

    private ViewModelLifecycle viewModelLifecycle;

    private ViewModelCBuilder(SingletonCImpl singletonCImpl,
        ActivityRetainedCImpl activityRetainedCImpl) {
      this.singletonCImpl = singletonCImpl;
      this.activityRetainedCImpl = activityRetainedCImpl;
    }

    @Override
    public ViewModelCBuilder savedStateHandle(SavedStateHandle handle) {
      this.savedStateHandle = Preconditions.checkNotNull(handle);
      return this;
    }

    @Override
    public ViewModelCBuilder viewModelLifecycle(ViewModelLifecycle viewModelLifecycle) {
      this.viewModelLifecycle = Preconditions.checkNotNull(viewModelLifecycle);
      return this;
    }

    @Override
    public CMMSApplication_HiltComponents.ViewModelC build() {
      Preconditions.checkBuilderRequirement(savedStateHandle, SavedStateHandle.class);
      Preconditions.checkBuilderRequirement(viewModelLifecycle, ViewModelLifecycle.class);
      return new ViewModelCImpl(singletonCImpl, activityRetainedCImpl, savedStateHandle, viewModelLifecycle);
    }
  }

  private static final class ServiceCBuilder implements CMMSApplication_HiltComponents.ServiceC.Builder {
    private final SingletonCImpl singletonCImpl;

    private Service service;

    private ServiceCBuilder(SingletonCImpl singletonCImpl) {
      this.singletonCImpl = singletonCImpl;
    }

    @Override
    public ServiceCBuilder service(Service service) {
      this.service = Preconditions.checkNotNull(service);
      return this;
    }

    @Override
    public CMMSApplication_HiltComponents.ServiceC build() {
      Preconditions.checkBuilderRequirement(service, Service.class);
      return new ServiceCImpl(singletonCImpl, service);
    }
  }

  private static final class ViewWithFragmentCImpl extends CMMSApplication_HiltComponents.ViewWithFragmentC {
    private final SingletonCImpl singletonCImpl;

    private final ActivityRetainedCImpl activityRetainedCImpl;

    private final ActivityCImpl activityCImpl;

    private final FragmentCImpl fragmentCImpl;

    private final ViewWithFragmentCImpl viewWithFragmentCImpl = this;

    private ViewWithFragmentCImpl(SingletonCImpl singletonCImpl,
        ActivityRetainedCImpl activityRetainedCImpl, ActivityCImpl activityCImpl,
        FragmentCImpl fragmentCImpl, View viewParam) {
      this.singletonCImpl = singletonCImpl;
      this.activityRetainedCImpl = activityRetainedCImpl;
      this.activityCImpl = activityCImpl;
      this.fragmentCImpl = fragmentCImpl;


    }
  }

  private static final class FragmentCImpl extends CMMSApplication_HiltComponents.FragmentC {
    private final SingletonCImpl singletonCImpl;

    private final ActivityRetainedCImpl activityRetainedCImpl;

    private final ActivityCImpl activityCImpl;

    private final FragmentCImpl fragmentCImpl = this;

    private FragmentCImpl(SingletonCImpl singletonCImpl,
        ActivityRetainedCImpl activityRetainedCImpl, ActivityCImpl activityCImpl,
        Fragment fragmentParam) {
      this.singletonCImpl = singletonCImpl;
      this.activityRetainedCImpl = activityRetainedCImpl;
      this.activityCImpl = activityCImpl;


    }

    @Override
    public DefaultViewModelFactories.InternalFactoryFactory getHiltInternalFactoryFactory() {
      return activityCImpl.getHiltInternalFactoryFactory();
    }

    @Override
    public ViewWithFragmentComponentBuilder viewWithFragmentComponentBuilder() {
      return new ViewWithFragmentCBuilder(singletonCImpl, activityRetainedCImpl, activityCImpl, fragmentCImpl);
    }
  }

  private static final class ViewCImpl extends CMMSApplication_HiltComponents.ViewC {
    private final SingletonCImpl singletonCImpl;

    private final ActivityRetainedCImpl activityRetainedCImpl;

    private final ActivityCImpl activityCImpl;

    private final ViewCImpl viewCImpl = this;

    private ViewCImpl(SingletonCImpl singletonCImpl, ActivityRetainedCImpl activityRetainedCImpl,
        ActivityCImpl activityCImpl, View viewParam) {
      this.singletonCImpl = singletonCImpl;
      this.activityRetainedCImpl = activityRetainedCImpl;
      this.activityCImpl = activityCImpl;


    }
  }

  private static final class ActivityCImpl extends CMMSApplication_HiltComponents.ActivityC {
    private final SingletonCImpl singletonCImpl;

    private final ActivityRetainedCImpl activityRetainedCImpl;

    private final ActivityCImpl activityCImpl = this;

    private ActivityCImpl(SingletonCImpl singletonCImpl,
        ActivityRetainedCImpl activityRetainedCImpl, Activity activityParam) {
      this.singletonCImpl = singletonCImpl;
      this.activityRetainedCImpl = activityRetainedCImpl;


    }

    @Override
    public void injectMainActivity(MainActivity mainActivity) {
      injectMainActivity2(mainActivity);
    }

    @Override
    public DefaultViewModelFactories.InternalFactoryFactory getHiltInternalFactoryFactory() {
      return DefaultViewModelFactories_InternalFactoryFactory_Factory.newInstance(getViewModelKeys(), new ViewModelCBuilder(singletonCImpl, activityRetainedCImpl));
    }

    @Override
    public Set<String> getViewModelKeys() {
      return SetBuilder.<String>newSetBuilder(16).add(AssetDetailViewModel_HiltModules_KeyModule_ProvideFactory.provide()).add(AssetsViewModel_HiltModules_KeyModule_ProvideFactory.provide()).add(CreateAssetViewModel_HiltModules_KeyModule_ProvideFactory.provide()).add(CreateInventoryViewModel_HiltModules_KeyModule_ProvideFactory.provide()).add(CreateWorksheetViewModel_HiltModules_KeyModule_ProvideFactory.provide()).add(DashboardViewModel_HiltModules_KeyModule_ProvideFactory.provide()).add(InventoryDetailViewModel_HiltModules_KeyModule_ProvideFactory.provide()).add(InventoryViewModel_HiltModules_KeyModule_ProvideFactory.provide()).add(LoginViewModel_HiltModules_KeyModule_ProvideFactory.provide()).add(MachineDetailViewModel_HiltModules_KeyModule_ProvideFactory.provide()).add(MachinesViewModel_HiltModules_KeyModule_ProvideFactory.provide()).add(PMViewModel_HiltModules_KeyModule_ProvideFactory.provide()).add(ReportsViewModel_HiltModules_KeyModule_ProvideFactory.provide()).add(SettingsViewModel_HiltModules_KeyModule_ProvideFactory.provide()).add(WorksheetDetailViewModel_HiltModules_KeyModule_ProvideFactory.provide()).add(WorksheetsViewModel_HiltModules_KeyModule_ProvideFactory.provide()).build();
    }

    @Override
    public ViewModelComponentBuilder getViewModelComponentBuilder() {
      return new ViewModelCBuilder(singletonCImpl, activityRetainedCImpl);
    }

    @Override
    public FragmentComponentBuilder fragmentComponentBuilder() {
      return new FragmentCBuilder(singletonCImpl, activityRetainedCImpl, activityCImpl);
    }

    @Override
    public ViewComponentBuilder viewComponentBuilder() {
      return new ViewCBuilder(singletonCImpl, activityRetainedCImpl, activityCImpl);
    }

    @CanIgnoreReturnValue
    private MainActivity injectMainActivity2(MainActivity instance) {
      MainActivity_MembersInjector.injectTokenManager(instance, singletonCImpl.provideTokenManagerProvider.get());
      return instance;
    }
  }

  private static final class ViewModelCImpl extends CMMSApplication_HiltComponents.ViewModelC {
    private final SingletonCImpl singletonCImpl;

    private final ActivityRetainedCImpl activityRetainedCImpl;

    private final ViewModelCImpl viewModelCImpl = this;

    private Provider<AssetDetailViewModel> assetDetailViewModelProvider;

    private Provider<AssetsViewModel> assetsViewModelProvider;

    private Provider<CreateAssetViewModel> createAssetViewModelProvider;

    private Provider<CreateInventoryViewModel> createInventoryViewModelProvider;

    private Provider<CreateWorksheetViewModel> createWorksheetViewModelProvider;

    private Provider<DashboardViewModel> dashboardViewModelProvider;

    private Provider<InventoryDetailViewModel> inventoryDetailViewModelProvider;

    private Provider<InventoryViewModel> inventoryViewModelProvider;

    private Provider<LoginViewModel> loginViewModelProvider;

    private Provider<MachineDetailViewModel> machineDetailViewModelProvider;

    private Provider<MachinesViewModel> machinesViewModelProvider;

    private Provider<PMViewModel> pMViewModelProvider;

    private Provider<ReportsViewModel> reportsViewModelProvider;

    private Provider<SettingsViewModel> settingsViewModelProvider;

    private Provider<WorksheetDetailViewModel> worksheetDetailViewModelProvider;

    private Provider<WorksheetsViewModel> worksheetsViewModelProvider;

    private ViewModelCImpl(SingletonCImpl singletonCImpl,
        ActivityRetainedCImpl activityRetainedCImpl, SavedStateHandle savedStateHandleParam,
        ViewModelLifecycle viewModelLifecycleParam) {
      this.singletonCImpl = singletonCImpl;
      this.activityRetainedCImpl = activityRetainedCImpl;

      initialize(savedStateHandleParam, viewModelLifecycleParam);

    }

    private GetAssetsUseCase getAssetsUseCase() {
      return new GetAssetsUseCase(singletonCImpl.provideAssetRepositoryProvider.get());
    }

    private RefreshAssetsUseCase refreshAssetsUseCase() {
      return new RefreshAssetsUseCase(singletonCImpl.provideAssetRepositoryProvider.get());
    }

    private GetInventoryUseCase getInventoryUseCase() {
      return new GetInventoryUseCase(singletonCImpl.provideInventoryRepositoryProvider.get());
    }

    private RefreshInventoryUseCase refreshInventoryUseCase() {
      return new RefreshInventoryUseCase(singletonCImpl.provideInventoryRepositoryProvider.get());
    }

    private LoginUseCase loginUseCase() {
      return new LoginUseCase(singletonCImpl.provideAuthRepositoryProvider.get());
    }

    @SuppressWarnings("unchecked")
    private void initialize(final SavedStateHandle savedStateHandleParam,
        final ViewModelLifecycle viewModelLifecycleParam) {
      this.assetDetailViewModelProvider = new SwitchingProvider<>(singletonCImpl, activityRetainedCImpl, viewModelCImpl, 0);
      this.assetsViewModelProvider = new SwitchingProvider<>(singletonCImpl, activityRetainedCImpl, viewModelCImpl, 1);
      this.createAssetViewModelProvider = new SwitchingProvider<>(singletonCImpl, activityRetainedCImpl, viewModelCImpl, 2);
      this.createInventoryViewModelProvider = new SwitchingProvider<>(singletonCImpl, activityRetainedCImpl, viewModelCImpl, 3);
      this.createWorksheetViewModelProvider = new SwitchingProvider<>(singletonCImpl, activityRetainedCImpl, viewModelCImpl, 4);
      this.dashboardViewModelProvider = new SwitchingProvider<>(singletonCImpl, activityRetainedCImpl, viewModelCImpl, 5);
      this.inventoryDetailViewModelProvider = new SwitchingProvider<>(singletonCImpl, activityRetainedCImpl, viewModelCImpl, 6);
      this.inventoryViewModelProvider = new SwitchingProvider<>(singletonCImpl, activityRetainedCImpl, viewModelCImpl, 7);
      this.loginViewModelProvider = new SwitchingProvider<>(singletonCImpl, activityRetainedCImpl, viewModelCImpl, 8);
      this.machineDetailViewModelProvider = new SwitchingProvider<>(singletonCImpl, activityRetainedCImpl, viewModelCImpl, 9);
      this.machinesViewModelProvider = new SwitchingProvider<>(singletonCImpl, activityRetainedCImpl, viewModelCImpl, 10);
      this.pMViewModelProvider = new SwitchingProvider<>(singletonCImpl, activityRetainedCImpl, viewModelCImpl, 11);
      this.reportsViewModelProvider = new SwitchingProvider<>(singletonCImpl, activityRetainedCImpl, viewModelCImpl, 12);
      this.settingsViewModelProvider = new SwitchingProvider<>(singletonCImpl, activityRetainedCImpl, viewModelCImpl, 13);
      this.worksheetDetailViewModelProvider = new SwitchingProvider<>(singletonCImpl, activityRetainedCImpl, viewModelCImpl, 14);
      this.worksheetsViewModelProvider = new SwitchingProvider<>(singletonCImpl, activityRetainedCImpl, viewModelCImpl, 15);
    }

    @Override
    public Map<String, Provider<ViewModel>> getHiltViewModelMap() {
      return MapBuilder.<String, Provider<ViewModel>>newMapBuilder(16).put("com.artence.cmms.ui.screens.assets.detail.AssetDetailViewModel", ((Provider) assetDetailViewModelProvider)).put("com.artence.cmms.ui.screens.assets.AssetsViewModel", ((Provider) assetsViewModelProvider)).put("com.artence.cmms.ui.screens.assets.create.CreateAssetViewModel", ((Provider) createAssetViewModelProvider)).put("com.artence.cmms.ui.screens.inventory.create.CreateInventoryViewModel", ((Provider) createInventoryViewModelProvider)).put("com.artence.cmms.ui.screens.worksheets.create.CreateWorksheetViewModel", ((Provider) createWorksheetViewModelProvider)).put("com.artence.cmms.ui.screens.dashboard.DashboardViewModel", ((Provider) dashboardViewModelProvider)).put("com.artence.cmms.ui.screens.inventory.detail.InventoryDetailViewModel", ((Provider) inventoryDetailViewModelProvider)).put("com.artence.cmms.ui.screens.inventory.InventoryViewModel", ((Provider) inventoryViewModelProvider)).put("com.artence.cmms.ui.screens.login.LoginViewModel", ((Provider) loginViewModelProvider)).put("com.artence.cmms.ui.screens.machines.detail.MachineDetailViewModel", ((Provider) machineDetailViewModelProvider)).put("com.artence.cmms.ui.screens.machines.MachinesViewModel", ((Provider) machinesViewModelProvider)).put("com.artence.cmms.ui.screens.pm.PMViewModel", ((Provider) pMViewModelProvider)).put("com.artence.cmms.ui.screens.reports.ReportsViewModel", ((Provider) reportsViewModelProvider)).put("com.artence.cmms.ui.screens.settings.SettingsViewModel", ((Provider) settingsViewModelProvider)).put("com.artence.cmms.ui.screens.worksheets.detail.WorksheetDetailViewModel", ((Provider) worksheetDetailViewModelProvider)).put("com.artence.cmms.ui.screens.worksheets.WorksheetsViewModel", ((Provider) worksheetsViewModelProvider)).build();
    }

    @Override
    public Map<String, Object> getHiltViewModelAssistedMap() {
      return Collections.<String, Object>emptyMap();
    }

    private static final class SwitchingProvider<T> implements Provider<T> {
      private final SingletonCImpl singletonCImpl;

      private final ActivityRetainedCImpl activityRetainedCImpl;

      private final ViewModelCImpl viewModelCImpl;

      private final int id;

      SwitchingProvider(SingletonCImpl singletonCImpl, ActivityRetainedCImpl activityRetainedCImpl,
          ViewModelCImpl viewModelCImpl, int id) {
        this.singletonCImpl = singletonCImpl;
        this.activityRetainedCImpl = activityRetainedCImpl;
        this.viewModelCImpl = viewModelCImpl;
        this.id = id;
      }

      @SuppressWarnings("unchecked")
      @Override
      public T get() {
        switch (id) {
          case 0: // com.artence.cmms.ui.screens.assets.detail.AssetDetailViewModel 
          return (T) new AssetDetailViewModel(singletonCImpl.provideAssetRepositoryProvider.get());

          case 1: // com.artence.cmms.ui.screens.assets.AssetsViewModel 
          return (T) new AssetsViewModel(viewModelCImpl.getAssetsUseCase(), viewModelCImpl.refreshAssetsUseCase());

          case 2: // com.artence.cmms.ui.screens.assets.create.CreateAssetViewModel 
          return (T) new CreateAssetViewModel(singletonCImpl.provideAssetRepositoryProvider.get());

          case 3: // com.artence.cmms.ui.screens.inventory.create.CreateInventoryViewModel 
          return (T) new CreateInventoryViewModel(singletonCImpl.provideInventoryRepositoryProvider.get());

          case 4: // com.artence.cmms.ui.screens.worksheets.create.CreateWorksheetViewModel 
          return (T) new CreateWorksheetViewModel(singletonCImpl.provideWorksheetRepositoryProvider.get());

          case 5: // com.artence.cmms.ui.screens.dashboard.DashboardViewModel 
          return (T) new DashboardViewModel();

          case 6: // com.artence.cmms.ui.screens.inventory.detail.InventoryDetailViewModel 
          return (T) new InventoryDetailViewModel(singletonCImpl.provideInventoryRepositoryProvider.get());

          case 7: // com.artence.cmms.ui.screens.inventory.InventoryViewModel 
          return (T) new InventoryViewModel(viewModelCImpl.getInventoryUseCase(), viewModelCImpl.refreshInventoryUseCase());

          case 8: // com.artence.cmms.ui.screens.login.LoginViewModel 
          return (T) new LoginViewModel(viewModelCImpl.loginUseCase());

          case 9: // com.artence.cmms.ui.screens.machines.detail.MachineDetailViewModel 
          return (T) new MachineDetailViewModel(singletonCImpl.provideMachineRepositoryProvider.get());

          case 10: // com.artence.cmms.ui.screens.machines.MachinesViewModel 
          return (T) new MachinesViewModel();

          case 11: // com.artence.cmms.ui.screens.pm.PMViewModel 
          return (T) new PMViewModel(singletonCImpl.providePMRepositoryProvider.get());

          case 12: // com.artence.cmms.ui.screens.reports.ReportsViewModel 
          return (T) new ReportsViewModel(singletonCImpl.provideReportsRepositoryProvider.get());

          case 13: // com.artence.cmms.ui.screens.settings.SettingsViewModel 
          return (T) new SettingsViewModel(singletonCImpl.provideTokenManagerProvider.get());

          case 14: // com.artence.cmms.ui.screens.worksheets.detail.WorksheetDetailViewModel 
          return (T) new WorksheetDetailViewModel(singletonCImpl.provideWorksheetRepositoryProvider.get());

          case 15: // com.artence.cmms.ui.screens.worksheets.WorksheetsViewModel 
          return (T) new WorksheetsViewModel();

          default: throw new AssertionError(id);
        }
      }
    }
  }

  private static final class ActivityRetainedCImpl extends CMMSApplication_HiltComponents.ActivityRetainedC {
    private final SingletonCImpl singletonCImpl;

    private final ActivityRetainedCImpl activityRetainedCImpl = this;

    private Provider<ActivityRetainedLifecycle> provideActivityRetainedLifecycleProvider;

    private ActivityRetainedCImpl(SingletonCImpl singletonCImpl,
        SavedStateHandleHolder savedStateHandleHolderParam) {
      this.singletonCImpl = singletonCImpl;

      initialize(savedStateHandleHolderParam);

    }

    @SuppressWarnings("unchecked")
    private void initialize(final SavedStateHandleHolder savedStateHandleHolderParam) {
      this.provideActivityRetainedLifecycleProvider = DoubleCheck.provider(new SwitchingProvider<ActivityRetainedLifecycle>(singletonCImpl, activityRetainedCImpl, 0));
    }

    @Override
    public ActivityComponentBuilder activityComponentBuilder() {
      return new ActivityCBuilder(singletonCImpl, activityRetainedCImpl);
    }

    @Override
    public ActivityRetainedLifecycle getActivityRetainedLifecycle() {
      return provideActivityRetainedLifecycleProvider.get();
    }

    private static final class SwitchingProvider<T> implements Provider<T> {
      private final SingletonCImpl singletonCImpl;

      private final ActivityRetainedCImpl activityRetainedCImpl;

      private final int id;

      SwitchingProvider(SingletonCImpl singletonCImpl, ActivityRetainedCImpl activityRetainedCImpl,
          int id) {
        this.singletonCImpl = singletonCImpl;
        this.activityRetainedCImpl = activityRetainedCImpl;
        this.id = id;
      }

      @SuppressWarnings("unchecked")
      @Override
      public T get() {
        switch (id) {
          case 0: // dagger.hilt.android.ActivityRetainedLifecycle 
          return (T) ActivityRetainedComponentManager_LifecycleModule_ProvideActivityRetainedLifecycleFactory.provideActivityRetainedLifecycle();

          default: throw new AssertionError(id);
        }
      }
    }
  }

  private static final class ServiceCImpl extends CMMSApplication_HiltComponents.ServiceC {
    private final SingletonCImpl singletonCImpl;

    private final ServiceCImpl serviceCImpl = this;

    private ServiceCImpl(SingletonCImpl singletonCImpl, Service serviceParam) {
      this.singletonCImpl = singletonCImpl;


    }
  }

  private static final class SingletonCImpl extends CMMSApplication_HiltComponents.SingletonC {
    private final ApplicationContextModule applicationContextModule;

    private final SingletonCImpl singletonCImpl = this;

    private Provider<TokenManager> provideTokenManagerProvider;

    private Provider<HttpLoggingInterceptor> provideLoggingInterceptorProvider;

    private Provider<OkHttpClient> provideOkHttpClientProvider;

    private Provider<Retrofit> provideRetrofitProvider;

    private Provider<AssetApi> provideAssetApiProvider;

    private Provider<CMMSDatabase> provideCMMSDatabaseProvider;

    private Provider<AssetDao> provideAssetDaoProvider;

    private Provider<AssetRepository> provideAssetRepositoryProvider;

    private Provider<InventoryApi> provideInventoryApiProvider;

    private Provider<InventoryDao> provideInventoryDaoProvider;

    private Provider<InventoryRepository> provideInventoryRepositoryProvider;

    private Provider<WorksheetApi> provideWorksheetApiProvider;

    private Provider<WorksheetDao> provideWorksheetDaoProvider;

    private Provider<WorksheetRepository> provideWorksheetRepositoryProvider;

    private Provider<AuthApi> provideAuthApiProvider;

    private Provider<AuthRepository> provideAuthRepositoryProvider;

    private Provider<MachineDao> provideMachineDaoProvider;

    private Provider<MachineApi> provideMachineApiProvider;

    private Provider<MachineRepository> provideMachineRepositoryProvider;

    private Provider<PMApi> providePMApiProvider;

    private Provider<PMTaskDao> providePMTaskDaoProvider;

    private Provider<PMRepository> providePMRepositoryProvider;

    private Provider<ReportsApi> provideReportsApiProvider;

    private Provider<ReportsRepository> provideReportsRepositoryProvider;

    private SingletonCImpl(ApplicationContextModule applicationContextModuleParam) {
      this.applicationContextModule = applicationContextModuleParam;
      initialize(applicationContextModuleParam);

    }

    @SuppressWarnings("unchecked")
    private void initialize(final ApplicationContextModule applicationContextModuleParam) {
      this.provideTokenManagerProvider = DoubleCheck.provider(new SwitchingProvider<TokenManager>(singletonCImpl, 0));
      this.provideLoggingInterceptorProvider = DoubleCheck.provider(new SwitchingProvider<HttpLoggingInterceptor>(singletonCImpl, 5));
      this.provideOkHttpClientProvider = DoubleCheck.provider(new SwitchingProvider<OkHttpClient>(singletonCImpl, 4));
      this.provideRetrofitProvider = DoubleCheck.provider(new SwitchingProvider<Retrofit>(singletonCImpl, 3));
      this.provideAssetApiProvider = DoubleCheck.provider(new SwitchingProvider<AssetApi>(singletonCImpl, 2));
      this.provideCMMSDatabaseProvider = DoubleCheck.provider(new SwitchingProvider<CMMSDatabase>(singletonCImpl, 7));
      this.provideAssetDaoProvider = DoubleCheck.provider(new SwitchingProvider<AssetDao>(singletonCImpl, 6));
      this.provideAssetRepositoryProvider = DoubleCheck.provider(new SwitchingProvider<AssetRepository>(singletonCImpl, 1));
      this.provideInventoryApiProvider = DoubleCheck.provider(new SwitchingProvider<InventoryApi>(singletonCImpl, 9));
      this.provideInventoryDaoProvider = DoubleCheck.provider(new SwitchingProvider<InventoryDao>(singletonCImpl, 10));
      this.provideInventoryRepositoryProvider = DoubleCheck.provider(new SwitchingProvider<InventoryRepository>(singletonCImpl, 8));
      this.provideWorksheetApiProvider = DoubleCheck.provider(new SwitchingProvider<WorksheetApi>(singletonCImpl, 12));
      this.provideWorksheetDaoProvider = DoubleCheck.provider(new SwitchingProvider<WorksheetDao>(singletonCImpl, 13));
      this.provideWorksheetRepositoryProvider = DoubleCheck.provider(new SwitchingProvider<WorksheetRepository>(singletonCImpl, 11));
      this.provideAuthApiProvider = DoubleCheck.provider(new SwitchingProvider<AuthApi>(singletonCImpl, 15));
      this.provideAuthRepositoryProvider = DoubleCheck.provider(new SwitchingProvider<AuthRepository>(singletonCImpl, 14));
      this.provideMachineDaoProvider = DoubleCheck.provider(new SwitchingProvider<MachineDao>(singletonCImpl, 17));
      this.provideMachineApiProvider = DoubleCheck.provider(new SwitchingProvider<MachineApi>(singletonCImpl, 18));
      this.provideMachineRepositoryProvider = DoubleCheck.provider(new SwitchingProvider<MachineRepository>(singletonCImpl, 16));
      this.providePMApiProvider = DoubleCheck.provider(new SwitchingProvider<PMApi>(singletonCImpl, 20));
      this.providePMTaskDaoProvider = DoubleCheck.provider(new SwitchingProvider<PMTaskDao>(singletonCImpl, 21));
      this.providePMRepositoryProvider = DoubleCheck.provider(new SwitchingProvider<PMRepository>(singletonCImpl, 19));
      this.provideReportsApiProvider = DoubleCheck.provider(new SwitchingProvider<ReportsApi>(singletonCImpl, 23));
      this.provideReportsRepositoryProvider = DoubleCheck.provider(new SwitchingProvider<ReportsRepository>(singletonCImpl, 22));
    }

    @Override
    public void injectCMMSApplication(CMMSApplication cMMSApplication) {
    }

    @Override
    public Set<Boolean> getDisableFragmentGetContextFix() {
      return Collections.<Boolean>emptySet();
    }

    @Override
    public ActivityRetainedComponentBuilder retainedComponentBuilder() {
      return new ActivityRetainedCBuilder(singletonCImpl);
    }

    @Override
    public ServiceComponentBuilder serviceComponentBuilder() {
      return new ServiceCBuilder(singletonCImpl);
    }

    private static final class SwitchingProvider<T> implements Provider<T> {
      private final SingletonCImpl singletonCImpl;

      private final int id;

      SwitchingProvider(SingletonCImpl singletonCImpl, int id) {
        this.singletonCImpl = singletonCImpl;
        this.id = id;
      }

      @SuppressWarnings("unchecked")
      @Override
      public T get() {
        switch (id) {
          case 0: // com.artence.cmms.data.local.datastore.TokenManager 
          return (T) AppModule_ProvideTokenManagerFactory.provideTokenManager(ApplicationContextModule_ProvideContextFactory.provideContext(singletonCImpl.applicationContextModule));

          case 1: // com.artence.cmms.data.repository.AssetRepository 
          return (T) AppModule_ProvideAssetRepositoryFactory.provideAssetRepository(singletonCImpl.provideAssetApiProvider.get(), singletonCImpl.provideAssetDaoProvider.get());

          case 2: // com.artence.cmms.data.remote.api.AssetApi 
          return (T) AppModule_ProvideAssetApiFactory.provideAssetApi(singletonCImpl.provideRetrofitProvider.get());

          case 3: // retrofit2.Retrofit 
          return (T) AppModule_ProvideRetrofitFactory.provideRetrofit(singletonCImpl.provideOkHttpClientProvider.get());

          case 4: // okhttp3.OkHttpClient 
          return (T) AppModule_ProvideOkHttpClientFactory.provideOkHttpClient(singletonCImpl.provideLoggingInterceptorProvider.get(), singletonCImpl.provideTokenManagerProvider.get(), ApplicationContextModule_ProvideContextFactory.provideContext(singletonCImpl.applicationContextModule));

          case 5: // okhttp3.logging.HttpLoggingInterceptor 
          return (T) AppModule_ProvideLoggingInterceptorFactory.provideLoggingInterceptor();

          case 6: // com.artence.cmms.data.local.database.dao.AssetDao 
          return (T) AppModule_ProvideAssetDaoFactory.provideAssetDao(singletonCImpl.provideCMMSDatabaseProvider.get());

          case 7: // com.artence.cmms.data.local.database.CMMSDatabase 
          return (T) AppModule_ProvideCMMSDatabaseFactory.provideCMMSDatabase(ApplicationContextModule_ProvideApplicationFactory.provideApplication(singletonCImpl.applicationContextModule));

          case 8: // com.artence.cmms.data.repository.InventoryRepository 
          return (T) AppModule_ProvideInventoryRepositoryFactory.provideInventoryRepository(singletonCImpl.provideInventoryApiProvider.get(), singletonCImpl.provideInventoryDaoProvider.get());

          case 9: // com.artence.cmms.data.remote.api.InventoryApi 
          return (T) AppModule_ProvideInventoryApiFactory.provideInventoryApi(singletonCImpl.provideRetrofitProvider.get());

          case 10: // com.artence.cmms.data.local.database.dao.InventoryDao 
          return (T) AppModule_ProvideInventoryDaoFactory.provideInventoryDao(singletonCImpl.provideCMMSDatabaseProvider.get());

          case 11: // com.artence.cmms.data.repository.WorksheetRepository 
          return (T) AppModule_ProvideWorksheetRepositoryFactory.provideWorksheetRepository(singletonCImpl.provideWorksheetApiProvider.get(), singletonCImpl.provideWorksheetDaoProvider.get());

          case 12: // com.artence.cmms.data.remote.api.WorksheetApi 
          return (T) AppModule_ProvideWorksheetApiFactory.provideWorksheetApi(singletonCImpl.provideRetrofitProvider.get());

          case 13: // com.artence.cmms.data.local.database.dao.WorksheetDao 
          return (T) AppModule_ProvideWorksheetDaoFactory.provideWorksheetDao(singletonCImpl.provideCMMSDatabaseProvider.get());

          case 14: // com.artence.cmms.data.repository.AuthRepository 
          return (T) AppModule_ProvideAuthRepositoryFactory.provideAuthRepository(singletonCImpl.provideAuthApiProvider.get(), singletonCImpl.provideTokenManagerProvider.get());

          case 15: // com.artence.cmms.data.remote.api.AuthApi 
          return (T) AppModule_ProvideAuthApiFactory.provideAuthApi(singletonCImpl.provideRetrofitProvider.get());

          case 16: // com.artence.cmms.data.repository.MachineRepository 
          return (T) AppModule_ProvideMachineRepositoryFactory.provideMachineRepository(singletonCImpl.provideMachineDaoProvider.get(), singletonCImpl.provideMachineApiProvider.get());

          case 17: // com.artence.cmms.data.local.database.dao.MachineDao 
          return (T) AppModule_ProvideMachineDaoFactory.provideMachineDao(singletonCImpl.provideCMMSDatabaseProvider.get());

          case 18: // com.artence.cmms.data.remote.api.MachineApi 
          return (T) AppModule_ProvideMachineApiFactory.provideMachineApi(singletonCImpl.provideRetrofitProvider.get());

          case 19: // com.artence.cmms.data.repository.PMRepository 
          return (T) AppModule_ProvidePMRepositoryFactory.providePMRepository(singletonCImpl.providePMApiProvider.get(), singletonCImpl.providePMTaskDaoProvider.get());

          case 20: // com.artence.cmms.data.remote.api.PMApi 
          return (T) AppModule_ProvidePMApiFactory.providePMApi(singletonCImpl.provideRetrofitProvider.get());

          case 21: // com.artence.cmms.data.local.database.dao.PMTaskDao 
          return (T) AppModule_ProvidePMTaskDaoFactory.providePMTaskDao(singletonCImpl.provideCMMSDatabaseProvider.get());

          case 22: // com.artence.cmms.data.repository.ReportsRepository 
          return (T) AppModule_ProvideReportsRepositoryFactory.provideReportsRepository(singletonCImpl.provideReportsApiProvider.get());

          case 23: // com.artence.cmms.data.remote.api.ReportsApi 
          return (T) AppModule_ProvideReportsApiFactory.provideReportsApi(singletonCImpl.provideRetrofitProvider.get());

          default: throw new AssertionError(id);
        }
      }
    }
  }
}
