from configDmanager import import_config


class RandomClass:
    def __init__(self, param1, param2, user_info, long_text):
        print(f"param1: {param1}")
        print(f"param2: {param2}")
        print(f'my user: {user_info.user}')
        print(f'my user: {user_info.password}')
        print(f'my long text: "{long_text[:40]}"')


config = import_config('MainConfig')

print("## Object 1")
obj = RandomClass(**config)


# You can also select specific keys
print("## Object 2")
another_obj = RandomClass(param2='Another Value', long_text="Not so long", **config[['param1', 'user_info']])
