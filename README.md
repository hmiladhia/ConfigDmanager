# ConfigDmanager

## Installation

A simple pip install will do :

```bash
python -m pip install ConfigDmanager
```

## Use

Suppose we have two Configuration files ( of json type ) :
- ParentConfig.json :

```json
{
"__name": "ParentConfig",
"param1": "Value 1"
}
```
- MainConfig.json :
  - The **__parent** parameter specifies the path to another configuration file that will give us default values ( Think of it as inheritance ). 
  - the text contained between brackets will be reinterpreted in runtime : {param1} -> Value 1
  - the use of environment variables for sensitive data like passwords is also possible : through this text {os_environ[password]}
```json
{
"__name": "MainConfig",
"__parent": "demo.ParentConfig",
"param2": "Value 2 and {param1}",
"user_info": {"user": "username", "password": "{os_environ[password]}"}
}
```



To import those configuration using **configDmanager**, use this demo code :

```python
from configDmanager import import_config


class RandomClass:
    def __init__(self, param1, param2, user_info):
        print(f"param1: {param1}")
        print(f"param2: {param2}")
        print(f'my user: {user_info.user}')
        print(f'my user: {user_info.password}')


config = import_config('MainConfig')

print("## Object 1")
obj = RandomClass(**config)


# You can also select specific keys
print("## Object 2")
another_obj = RandomClass(param2='Another Value', **config[['param1', 'user_info']])

```



