// EconViz API Gateway — ASP.NET Core entry point.
// Configures DI, middleware, SignalR hub, and routes.

var builder = WebApplication.CreateBuilder(args);

// TODO: register services
// builder.Services.AddSignalR();
// builder.Services.AddMemoryCache();
// builder.Services.AddHttpClient<PythonApiClient>();
// builder.Services.AddHostedService<RefreshScheduler>();
// builder.Services.AddControllers();

var app = builder.Build();

// TODO: configure middleware
// app.MapControllers();
// app.MapHub<MarketHub>("/hubs/market");

app.Run();
