import pytest

from configDmanager import import_config
from configDmanager.errors import ReinterpretationError


conf = import_config('configs.TestConfig')
fstring_conf = import_config('configs.FstringConfig')


def test_param_as_attribute():
    assert conf.mail_port == 587


def test_params_in_parent():
    assert conf.mail_use_tls


def test_sub_config():
    assert conf.user_info.user == "RandomName"


def test_params_as_keys():
    assert conf['mail_port'] == 587


def test_sub_config_as_keys():
    assert conf['user_info.user'] == "RandomName"


def get_params(**kwargs):
    return str(kwargs)


def test_dict_as_key():
    expected = {"{'mail_server': 'smtp.google.com', 'tls': True}", "{'tls': True, 'mail_server': 'smtp.google.com'}"}
    assert get_params(**conf[{'mail_server': 'mail_server', 'mail_use_tls': 'tls'}]) in expected


def test_iterable_as_key():
    expected = {"{'mail_server': 'smtp.google.com', 'mail_use_tls': True}",
                "{'mail_use_tls': True, 'mail_server': 'smtp.google.com'}"}
    assert get_params(**conf[{'mail_server', 'mail_use_tls'}]) in expected
    assert get_params(**conf[['mail_server', 'mail_use_tls']]) in expected
    assert get_params(**conf[('mail_server', 'mail_use_tls')]) in expected


def test_param_add_as_attr():
    with pytest.raises(AttributeError):
        conf.param1
    conf.param1 = 'value1'
    assert conf.param1 == "value1"
    assert conf['param1'] == "value1"


def test_param_add_as_key():
    with pytest.raises(AttributeError):
        conf.param2
    conf['param2'] = 'value2'
    assert conf.param2 == "value2"
    assert conf['param2'] == "value2"


def test_private_param_add_as_attr():
    with pytest.raises(AttributeError):
        result = conf.__param1
    conf.__param1 = 'value1'
    with pytest.raises(AttributeError):
        result = conf.__param1
    with pytest.raises(KeyError):
        result = conf['__param1']

    assert'__param1' in conf.to_dict()


def test_private_param_add_as_key():
    conf['__param2'] = 'value2'
    with pytest.raises(AttributeError):
        result = conf.__param2
    with pytest.raises(KeyError):
        result = conf['__param2']

    assert'__param2' in conf.to_dict()


def test_real_private_not_in_dict():
    assert '__config_dict' not in conf.to_dict()


def test_fstrings_works():
    assert fstring_conf['mail'] == 'RandomName@gmail.com'


def test_environ_var_works():
    assert fstring_conf['password'] == '123456'


def test_fstrings_recursion_error():
    with pytest.raises(ReinterpretationError) as context:
        result = fstring_conf.value1
    expected = {'Param (value1: {value2}) reinterpretation failed: Due to cycle - RecursionError',
                'Param (value2: {value1}) reinterpretation failed: Due to cycle - RecursionError'}
    assert str(context.value) in expected


def test_key_access_error_message():
    with pytest.raises(KeyError) as context:
        fstring_conf['po']
    assert str(context.value) == "\"Could not find param 'po' in FstringConfig\""


def test_environ_access_error_message():
    with pytest.raises(ReinterpretationError) as context:
        fstring_conf['mypassword']
    assert str(context.value) == "Param (mypassword: {os_environ[password]}) reinterpretation failed: Could not find 'password' in Environment variables"


def test_reinterpretation_key_access_error_message():
    with pytest.raises(ReinterpretationError) as context:
        fstring_conf['my_other_password']
    assert str(context.value) == "Param (my_other_password: {passwor}) reinterpretation failed: Could not find param 'passwor' in FstringConfig"


def test_attribute_access_error_message():
    with pytest.raises(AttributeError) as context:
        fstring_conf.po
    assert str(context.value) == "'Config' object has no attribute 'po'"


def test_file_integration_path_relative_to_cwd():
    result = fstring_conf.text2
    assert result.startswith("Cum saepe multa, tum memini domi in hemicyclio sedentem,")
    with open('long_text.txt', 'r') as file:
        expected = file.read()
    assert result == expected


def test_file_integration_path_relative_to_config():
    result = fstring_conf.text
    assert result.startswith("Cum saepe multa, tum memini domi in hemicyclio sedentem,")
    with open('long_text.txt', 'r') as file:
        expected = file.read()
    assert result == expected


def test_file_integration_error():
    with pytest.raises(ReinterpretationError) as context:
        fstring_conf.text3
    print(context.value)
    assert str(context.value) == "Param (text3: {read_file[missing.txt]}) reinterpretation failed: [Errno 2] No such file or directory: 'missing.txt'"
