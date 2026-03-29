// EconViz API Gateway — ASP.NET Core entry point.
// Configures DI, middleware, SignalR hub, and routes.

using System.Text.Json;
using EconViz.Gateway.Hubs;
using EconViz.Gateway.Services;

// --- Service Registration (DI) ---
var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers().AddJsonOptions(o =>
    o.JsonSerializerOptions.PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower);
builder.Services.AddMemoryCache();
builder.Services.AddSignalR();
builder.Services.AddSingleton<CacheService>();
builder.Services.AddHttpClient<PythonApiClient>(client =>
{
    client.BaseAddress = new Uri(builder.Configuration["PythonBackend:BaseUrl"]!);
});
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
