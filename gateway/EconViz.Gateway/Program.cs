// EconViz API Gateway — ASP.NET Core entry point.
// Configures DI, middleware, SignalR hub, and routes.

// --- Service Registration (DI) ---
// Each line tells ASP.NET how to create and inject dependencies.
// Order doesn't matter here — DI resolves at request time, not registration time.

// TODO: create builder via WebApplication.CreateBuilder(args)

// TODO: AddControllers() — enables controller classes to handle HTTP requests
//       Chain .AddJsonOptions() to set PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower
//       so C# PascalCase properties serialize/deserialize as snake_case to match Python JSON

// TODO: AddMemoryCache() — enables IMemoryCache for CacheService

// TODO: AddSignalR() — enables SignalR for real-time push via MarketHub

// TODO: AddSingleton<CacheService>() — registers CacheService as a singleton
//       (one instance shared across all requests, since the cache must persist)

// TODO: AddHttpClient<PythonApiClient>() — registers PythonApiClient with a configured HttpClient
//       Configure the HttpClient's BaseAddress from config: builder.Configuration["PythonBackend:BaseUrl"]

// TODO: AddHostedService<RefreshScheduler>() — starts the background refresh timer

// --- App Build & Middleware ---
// TODO: call builder.Build() to create the app

// TODO: MapControllers() — routes incoming HTTP requests to controller methods

// TODO: MapHub<MarketHub>("/hubs/market") — maps the SignalR hub to its URL

// TODO: app.Run() — starts the server
