// EconViz API Gateway — ASP.NET Core entry point.
// Configures DI, middleware, SignalR hub, and routes.

using System.Text.Json;
using EconViz.Gateway.Hubs;
using EconViz.Gateway.Services;

// --- Service Registration (DI) ---
// Each line tells ASP.NET how to create and inject dependencies.
// Order doesn't matter here — DI resolves at request time, not registration time.

// TODO: create builder via WebApplication.CreateBuilder(args)
var builder = WebApplication.CreateBuilder(args);
// TODO: AddControllers() — enables controller classes to handle HTTP requests
//       Chain .AddJsonOptions() to set PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower
//       so C# PascalCase properties serialize/deserialize as snake_case to match Python JSON
builder.Services.AddControllers().AddJsonOptions(o =>
    o.JsonSerializerOptions.PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower);
// TODO: AddMemoryCache() — enables IMemoryCache for CacheService
builder.Services.AddMemoryCache();
// TODO: AddSignalR() — enables SignalR for real-time push via MarketHub
builder.Services.AddSignalR();
// TODO: AddSingleton<CacheService>() — registers CacheService as a singleton
//       (one instance shared across all requests, since the cache must persist)
builder.Services.AddSingleton<CacheService>();
// TODO: AddHttpClient<PythonApiClient>() — registers PythonApiClient with a configured HttpClient
//       Configure the HttpClient's BaseAddress from config: builder.Configuration["PythonBackend:BaseUrl"]
builder.Services.AddHttpClient<PythonApiClient>(client =>
{
    client.BaseAddress = new Uri(builder.Configuration["PythonBackend:BaseUrl"]!);
});
// TODO: AddHostedService<RefreshScheduler>() — starts the background refresh timer
builder.Services.AddHostedService<RefreshScheduler>();
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.WithOrigins("http://localhost:3000", "http://localhost:3001", "http://localhost:3002")
              .AllowAnyHeader()
              .AllowAnyMethod()
              .AllowCredentials();
    });
});
// --- App Build & Middleware ---
var app = builder.Build();
app.UseCors();
app.MapControllers();
app.MapHub<MarketHub>("/hubs/market");
app.Run();