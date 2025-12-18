package com.artence.cmms.di

import android.app.Application
import android.content.Context
import androidx.room.Room
import com.artence.cmms.data.local.database.CMMSDatabase
import com.artence.cmms.data.local.database.dao.InventoryDao
import com.artence.cmms.data.local.database.dao.MachineDao
import com.artence.cmms.data.local.database.dao.PMTaskDao
import com.artence.cmms.data.local.database.dao.UserDao
import com.artence.cmms.data.local.database.dao.WorksheetDao
import com.artence.cmms.data.local.datastore.TokenManager
import com.artence.cmms.data.remote.api.AuthApi
import com.artence.cmms.data.remote.api.InventoryApi
import com.artence.cmms.data.remote.api.MachineApi
import com.artence.cmms.data.remote.api.PMApi
import com.artence.cmms.data.remote.api.AssetApi
import com.artence.cmms.data.remote.api.WorksheetApi
import com.artence.cmms.data.remote.api.UserApi
import com.artence.cmms.data.remote.api.ReportsApi
import com.artence.cmms.data.repository.AuthRepository
import com.artence.cmms.data.repository.MachineRepository
import com.artence.cmms.data.repository.PMRepository
import com.artence.cmms.data.repository.UserRepository
import com.artence.cmms.data.repository.ReportsRepository
import com.artence.cmms.util.Constants
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import okhttp3.Cache
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.io.File
import java.util.concurrent.TimeUnit
import javax.inject.Singleton
import kotlinx.coroutines.flow.first

@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    @Provides
    @Singleton
    fun provideLoggingInterceptor(): HttpLoggingInterceptor {
        return HttpLoggingInterceptor().setLevel(HttpLoggingInterceptor.Level.BODY)
    }

    @Provides
    @Singleton
    fun provideOkHttpClient(
        loggingInterceptor: HttpLoggingInterceptor,
        tokenManager: TokenManager,
        @ApplicationContext context: Context
    ): OkHttpClient {
        val httpCacheDir = File(context.cacheDir, "http_cache")
        val cacheSize = (10 * 1024 * 1024).toLong()
        val httpCache = Cache(httpCacheDir, cacheSize)

        return OkHttpClient.Builder()
            .addInterceptor { chain ->
                val original = chain.request()
                val requestBuilder = original.newBuilder()

                // Add Authorization header with Bearer token if available
                val token = kotlinx.coroutines.runBlocking {
                    tokenManager.getToken().first()
                }
                if (!token.isNullOrEmpty()) {
                    requestBuilder.header("Authorization", "Bearer $token")
                }

                chain.proceed(requestBuilder.build())
            }
            .addInterceptor(loggingInterceptor)
            .cache(httpCache)
            .connectTimeout(Constants.TIMEOUT_SECONDS, TimeUnit.SECONDS)
            .readTimeout(Constants.TIMEOUT_SECONDS, TimeUnit.SECONDS)
            .writeTimeout(Constants.TIMEOUT_SECONDS, TimeUnit.SECONDS)
            .build()
    }

    @Provides
    @Singleton
    fun provideRetrofit(client: OkHttpClient): Retrofit {
        return Retrofit.Builder()
            .baseUrl(Constants.BASE_URL)
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    @Provides
    @Singleton
    fun provideCMMSDatabase(app: Application): CMMSDatabase {
        return Room.databaseBuilder(
            app,
            CMMSDatabase::class.java,
            Constants.DATABASE_NAME
        ).build()
    }

    @Provides
    @Singleton
    fun provideAuthApi(retrofit: Retrofit): AuthApi = retrofit.create(AuthApi::class.java)

    @Provides
    @Singleton
    fun provideAssetApi(retrofit: Retrofit): AssetApi = retrofit.create(AssetApi::class.java)

    @Provides
    @Singleton
    fun provideWorksheetApi(retrofit: Retrofit): WorksheetApi = retrofit.create(WorksheetApi::class.java)

    @Provides
    @Singleton
    fun provideMachineApi(retrofit: Retrofit): MachineApi = retrofit.create(MachineApi::class.java)

    @Provides
    @Singleton
    fun provideInventoryApi(retrofit: Retrofit): InventoryApi = retrofit.create(InventoryApi::class.java)

    @Provides
    @Singleton
    fun providePMApi(retrofit: Retrofit): PMApi = retrofit.create(PMApi::class.java)

    @Provides
    @Singleton
    fun provideUserApi(retrofit: Retrofit): UserApi = retrofit.create(UserApi::class.java)

    @Provides
    @Singleton
    fun provideReportsApi(retrofit: Retrofit): ReportsApi = retrofit.create(ReportsApi::class.java)

    @Provides
    @Singleton
    fun provideUserDao(database: CMMSDatabase): UserDao = database.userDao()

    @Provides
    @Singleton
    fun provideMachineDao(database: CMMSDatabase): MachineDao = database.machineDao()

    @Provides
    @Singleton
    fun provideWorksheetDao(database: CMMSDatabase): WorksheetDao = database.worksheetDao()

    @Provides
    @Singleton
    fun provideAssetDao(database: CMMSDatabase): com.artence.cmms.data.local.database.dao.AssetDao = database.assetDao()

    @Provides
    @Singleton
    fun provideInventoryDao(database: CMMSDatabase): InventoryDao = database.inventoryDao()

    @Provides
    @Singleton
    fun providePMTaskDao(database: CMMSDatabase): PMTaskDao = database.pmTaskDao()

    @Provides
    @Singleton
    fun provideTokenManager(@ApplicationContext context: Context): TokenManager = TokenManager(context)

    @Provides
    @Singleton
    fun provideAuthRepository(
        authApi: AuthApi,
        tokenManager: TokenManager
    ): AuthRepository = AuthRepository(authApi, tokenManager)

    @Provides
    @Singleton
    fun provideUserRepository(
        userDao: UserDao,
        userApi: UserApi
    ): UserRepository = UserRepository(userDao, userApi)

    @Provides
    @Singleton
    fun provideMachineRepository(
        machineDao: MachineDao,
        machineApi: MachineApi
    ): MachineRepository = MachineRepository(machineDao, machineApi)

    @Provides
    @Singleton
    fun provideAssetRepository(
        assetApi: AssetApi,
        assetDao: com.artence.cmms.data.local.database.dao.AssetDao
    ): com.artence.cmms.data.repository.AssetRepository = com.artence.cmms.data.repository.AssetRepository(assetApi, assetDao)

    @Provides
    @Singleton
    fun provideWorksheetRepository(
        worksheetApi: WorksheetApi,
        worksheetDao: WorksheetDao
    ): com.artence.cmms.data.repository.WorksheetRepository = com.artence.cmms.data.repository.WorksheetRepository(worksheetApi, worksheetDao)

    @Provides
    @Singleton
    fun provideInventoryRepository(
        inventoryApi: InventoryApi,
        inventoryDao: InventoryDao
    ): com.artence.cmms.data.repository.InventoryRepository = com.artence.cmms.data.repository.InventoryRepository(inventoryDao, inventoryApi)

    @Provides
    @Singleton
    fun providePMRepository(
        pmApi: PMApi,
        pmTaskDao: PMTaskDao
    ): PMRepository = PMRepository(pmApi, pmTaskDao)

    @Provides
    @Singleton
    fun provideReportsRepository(
        reportsApi: ReportsApi
    ): ReportsRepository = ReportsRepository(reportsApi)
}
