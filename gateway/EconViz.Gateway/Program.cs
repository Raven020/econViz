// EconViz API Gateway — ASP.NET Core entry point.
// Configures DI, middleware, SignalR hub, and routes.

using System.Text.Json;
using Microsoft.AspNetCore.Diagnostics;
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
// Refresh runs as a standalone process via cron (see /etc/cron.d/econviz-refresh
// on the EC2 box) so it can't share the API server's DuckDB buffer manager.
// builder.Services.AddHostedService<RefreshScheduler>();
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.WithOrigins(
                  "http://localhost:3000",
                  "http://localhost:3001",
                  "http://localhost:3002",
                  "https://econviz.tech",
                  "https://www.econviz.tech")
              .AllowAnyHeader()
              .AllowAnyMethod()
              .AllowCredentials();
    });
});

// --- App Build & Middleware ---
var app = builder.Build();

// Translate backend HttpRequestException (e.g. Python 5xx) into 503 with
// Retry-After so the frontend retries cleanly instead of seeing a Kestrel-
// aborted connection.
app.UseExceptionHandler(handler =>
{
    handler.Run(async ctx =>
    {
        var ex = ctx.Features.Get<IExceptionHandlerFeature>()?.Error;
        if (ex is HttpRequestException)
        {
            ctx.Response.StatusCode = StatusCodes.Status503ServiceUnavailable;
            ctx.Response.Headers.Append("Retry-After", "30");
            await ctx.Response.WriteAsJsonAsync(new { error = "Backend temporarily unavailable" });
        }
        else
        {
            ctx.Response.StatusCode = StatusCodes.Status500InternalServerError;
            await ctx.Response.WriteAsJsonAsync(new { error = "Internal server error" });
        }
    });
});

app.UseCors();
app.MapControllers();
app.MapHub<MarketHub>("/hubs/market");
app.Run();
