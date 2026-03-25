// In-memory response caching for Python backend responses.
// Uses IMemoryCache with configurable TTLs per data type.

namespace EconViz.Gateway.Services;

public class CacheService
{
  private readonly IMemoryCache _cache;
  private readonly int _priceTtl;
  private readonly int _projectionTtl;

  public CacheService(IMemoryCache cache, IConfiguration config)
  {
    // stores into the cache and reads the TTLs
    _cache = cache;
    _priceTtl = config.GetValue<int>("Cache:PriceTtlSeconds");
    _projectionTtl = config.GetValue<int>("Cache:ProjectionTtlSeconds");
  }

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
  public void Invalidate(string key)
  {
      _cache.Remove(key);
  }
}
