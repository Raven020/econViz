// In-memory response caching for Python backend responses.
// Uses IMemoryCache with configurable TTLs per data type.

using Microsoft.Extensions.Caching.Memory;

namespace EconViz.Gateway.Services;

public class CacheService
{
    private readonly IMemoryCache _cache;
    private readonly int _priceTtl;
    private readonly int _projectionTtl;

    /// <summary>
    /// Constructor — receives IMemoryCache and reads TTL values from appsettings.json.
    /// "Cache:PriceTtlSeconds" (default 60) for price data.
    /// "Cache:ProjectionTtlSeconds" (default 300) for projection data.
    /// </summary>
    /// <param name="cache">ASP.NET in-memory cache instance</param>
    /// <param name="config">App configuration for reading TTL settings</param>
    public CacheService(IMemoryCache cache, IConfiguration config)
    {
        // stores into the cache and reads the TTLs
        _cache = cache;
        _priceTtl = config.GetValue<int>("Cache:PriceTtlSeconds", 60);
        _projectionTtl = config.GetValue<int>("Cache:ProjectionTtlSeconds", 300);
    }

    /// <summary>
    /// Returns cached value if present, otherwise calls fetch(), caches the result,
    /// and returns it. Uses the price TTL by default, or projection TTL if isProjection is true.
    /// </summary>
    /// <typeparam name="T">Type of the cached data</typeparam>
    /// <param name="key">Cache key (e.g. "instruments", "instrument_SPY", "projections_SPY")</param>
    /// <param name="fetch">Async function to call on cache miss (e.g. PythonApiClient method)</param>
    /// <param name="isProjection">If true, uses the longer projection TTL (300s) instead of price TTL (60s)</param>
    /// <returns>Cached or freshly fetched data of type T</returns>
    public async Task<T> GetOrSetAsync<T>(string key, Func<Task<T>> fetch, bool isProjection = false)
    {
        // if cached return stored value
        if (_cache.TryGetValue(key, out T cached))
            return cached;
        // if not fetch new value
        var result = await fetch();
        var ttl = isProjection ? _projectionTtl : _priceTtl;
        _cache.Set(key, result, TimeSpan.FromSeconds(ttl));
        return result;
    }

    /// <summary>
    /// Removes a cached entry by key. Called after a refresh to clear stale data.
    /// </summary>
    /// <param name="key">Cache key to remove (e.g. "instruments")</param>
    public void Invalidate(string key)
    {
        _cache.Remove(key);
    }
}
