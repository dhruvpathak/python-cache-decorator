# Python cache decorator / django cache decorator

## A python memcached decorator (or redis cache ) 

A decorator to be used with any caching backend e.g. memcached,redis etc to provide
flexible caching for multiple use cases without altering the original methods.
Can be used in plain python program using cache backends like pylibmc, python-memcached,
or frameworks like Django.

###Examples:


* Caching result of the method for 1 hour, based on all parameters to the method

```python
@cache_result(seconds=1*60*60)
def get_price(fruit, weight, some_other_key):
    rates = {'apple': 10,'banana': 15,'grapes':20}
    if fruit not in rates:
       return {'success': False, 'data' : 'RATE_NOT_FOUND_ERROR' }
    
    total_price = rates['fruit'] * weight
    return {'success': True,'data':total_price }
  
```

* Caching result of the method for 1 hour, based on selective parameters i.e. fruit & weight, irrespective of the
value of some_other_key

```python
@cache_result(cache_kwarg_keys=['fruit','weight'],seconds=1*60*60)
def get_price(fruit, weight, some_other_key):
    rates = {'apple': 10,'banana': 15,'grapes':20}
    if fruit not in rates:
       return {'success': False, 'data' : 'RATE_NOT_FOUND_ERROR' }
    
    total_price = rates['fruit'] * weight
    return {'success': True,'data':total_price }
    
```


* Caching result of the method for 1 hour, based on selective parameters i.e. fruit & weight, irrespective of the
value of some_other_key, and caching only in success cases, ignoring exception results or non-data cases,
in the below example, caching will only be done if the method returns 'success' key as True, and no caching
is done if 'success' is False

```python
@cache_result(cache_kwarg_keys=['fruit','weight'],seconds=1*60*60, cache_filter= lambda x:x['success'])
def get_price(fruit, weight, some_other_key):
    rates = {'apple': 10,'banana': 15,'grapes':20}
    if fruit not in rates:
       return {'success': False, 'data' : 'RATE_NOT_FOUND_ERROR' }
    
    total_price = rates['fruit'] * weight
    return {'success': True,'data':total_price }
```
