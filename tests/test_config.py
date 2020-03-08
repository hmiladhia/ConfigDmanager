import pytest

from configDmanager import import_config
from configDmanager.errors import ReinterpretationError


@pytest.fixture
def conf():
    return import_config('configs.TestConfig')


@pytest.fixture
def fstring_conf():
    return import_config('configs.FstringConfig')


@pytest.fixture
def yaml_conf():
    return import_config('configs.YamlConfig')


def test_param_as_attribute(conf):
    assert conf.mail_port == 587


def test_params_in_parent(conf):
    assert conf.mail_use_tls


def test_sub_config(conf):
    assert conf.user_info.user == "RandomName"


def test_params_as_keys(conf):
    assert conf['mail_port'] == 587


def test_sub_config_as_keys(conf):
    assert conf['user_info.user'] == "RandomName"


def get_params(**kwargs):
    return str(kwargs)


def test_dict_as_key(conf):
    expected = {"{'mail_server': 'smtp.google.com', 'tls': True}", "{'tls': True, 'mail_server': 'smtp.google.com'}"}
    assert get_params(**conf[{'mail_server': 'mail_server', 'mail_use_tls': 'tls'}]) in expected


@pytest.mark.parametrize('keys', [
    {'mail_server', 'mail_use_tls'},
    ['mail_server', 'mail_use_tls'],
    ('mail_server', 'mail_use_tls')])
def test_iterable_as_key(keys, conf):
    expected = {"{'mail_server': 'smtp.google.com', 'mail_use_tls': True}",
                "{'mail_use_tls': True, 'mail_server': 'smtp.google.com'}"}
    assert get_params(**conf[keys]) in expected


def test_param_add_as_attr(conf):
    with pytest.raises(AttributeError):
        conf.param1
    conf.param1 = 'value1'
    assert conf.param1 == "value1"
    assert conf['param1'] == "value1"


def test_param_add_as_key(conf):
    with pytest.raises(AttributeError):
        conf.param2
    conf['param2'] = 'value2'
    assert conf.param2 == "value2"
    assert conf['param2'] == "value2"


def test_private_param_add_as_attr(conf):
    with pytest.raises(AttributeError):
        conf.__param1
    conf.__param1 = 'value1'
    with pytest.raises(AttributeError):
        result = conf.__param1
    assert conf['__param1'] == 'value1'

    assert'__param1' in conf.to_dict(private=True)


def test_private_param_add_as_key(conf):
    conf['__param2'] = 'value2'
    with pytest.raises(AttributeError):
        result = conf.__param2
    result = conf['__param2'] == 'value2'

    assert'__param2' in conf.to_dict(private=True)


def test_real_private_not_in_dict(conf):
    assert '__config_dict' not in conf.to_dict(private=True)


def test_parent_param_not_in_dict(fstring_conf):
    assert 'mail_use_tls' not in fstring_conf.to_dict(private=True, include_parent=False)


def test_parent_param_in_dict_when_true(fstring_conf):
    assert 'mail_use_tls' in fstring_conf.to_dict(private=True, include_parent=True)


def test_private_not_in_dict(conf):
    conf.__param = 5
    assert '__param' not in conf.to_dict(private=False)


def test_fstrings_works(fstring_conf):
    assert fstring_conf['mail'] == 'RandomName@gmail.com'


def test_environ_var_works(fstring_conf):
    assert fstring_conf['password'] == '123456'


def test_fstrings_recursion_error(fstring_conf):
    with pytest.raises(ReinterpretationError) as context:
        fstring_conf.value1
    expected = {'Param (value1: ${value2}) reinterpretation failed: Due to cycle - RecursionError',
                'Param (value2: ${value1}) reinterpretation failed: Due to cycle - RecursionError'}
    assert str(context.value) in expected


# noinspection PyStatementEffect
@pytest.mark.parametrize("key, error_type, error_msg", [
    ('po', KeyError, "\"Could not find param 'po' in FstringConfig\""),  # test missing param error
    ('mypassword', ReinterpretationError, "Param (mypassword: "  # test missing environment param error
     "${os_environ[password]}) reinterpretation failed: Could not find 'password' in Environment variables"),
    ('my_other_password', ReinterpretationError,  # test missing param for reinpretation error
     "Param (my_other_password: ${passwor}) reinterpretation failed: Could not find param 'passwor' in FstringConfig"),
    ('text3', ReinterpretationError, "Param (text3: ${read_file[missing.txt]}) reinterpretation failed: [Errno 2] No "
                                     "such file or directory: 'missing.txt'")])  # test file integration error
def test_access_error_message(key, error_type, error_msg, fstring_conf):
    with pytest.raises(error_type) as context:
        fstring_conf[key]
    assert str(context.value) == error_msg


def test_reinterpretation_escape(fstring_conf):
    assert fstring_conf['value3'] == r"${Hello World}"


def test_attribute_access_error_message(fstring_conf):
    with pytest.raises(AttributeError) as context:
        fstring_conf.po
    assert str(context.value) == "'Config' object has no attribute 'po'"


@pytest.mark.parametrize('text_key', [
    'text2',  # test_path_relative_to_cwd
    'text'    # test_relative_to_config
])
def test_file_integration(text_key, fstring_conf):
    result = fstring_conf[text_key]
    assert result.startswith("Cum saepe multa, tum memini domi in hemicyclio sedentem,")
    with open('long_text.txt', 'r') as file:
        expected = file.read()
    assert result == expected


def test_yaml_subclass(yaml_conf):
    assert yaml_conf.subconfig.param1 == 'value1'


def test_sub_key_reinterpretation(fstring_conf):
    assert fstring_conf.version == "0.0.4"


@pytest.mark.parametrize("key", [158, [1, 2, 3]])
def test_param_setting(key, fstring_conf):
    with pytest.raises(TypeError) as context:
        fstring_conf[key] = "Test value"
    assert str(context.value) == 'Key should be of type str'


def test_sub_key_setting(fstring_conf):
    fstring_conf['__version.__patch'] = 8
    assert fstring_conf['__version.__patch'] == 8
