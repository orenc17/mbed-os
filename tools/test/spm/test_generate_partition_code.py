import re
import jsonschema.exceptions as jexcep
import pytest
from jinja2.defaults import DEFAULT_FILTERS

from test_data import *
from tools.spm.generate_partition_code import *

# Imported again as a module for monkey-patching
import tools.spm.generate_partition_code as generate_partition_code

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def extract_test_name(line):
    return re.search(r'.*\[(.*)\]', line).group(1)


def dump_manifest_to_json(manifest, test_name, test_dir, create_files=True):
    """
    Create a JSON manifest file from a dictionary.

    :param manifest: The manifest dictionary.
    :param test_name: Name of the test.
    :param test_dir: Directory to contain the JSON file.
    :param create_files: Whether to create the source files listed in the
           manifest 'source_files' entry.
    :return: Path of the JSON file.
    """
    test_file_name = test_dir.join('{}.json'.format(test_name))
    with open(test_file_name.strpath, 'wt') as fh:
        json.dump(manifest, fh, indent=2)

    # Create all the partition source files
    if create_files:
        [test_dir.join(name).write(name) for name in
         manifest.get('source_files', [])]

    return test_file_name.strpath


def find_priority_key(value):
    """
    Finds the key in 'Manifest.PRIORITY' of a given value.

    :param value: The value.
    :return: The key of the given value.
    """
    return next(
        (key for key, val in Manifest.PRIORITY.items() if val == value),
        None
    )


def find_permission_key(value):
    """
    Finds the key in 'MmioRegion.MMIO_PERMISIONS' of a given value.

    :param value: The value.
    :return: The key of the given value.
    """
    return next(
        (key for key, val in MmioRegion.MMIO_PERMISSIONS.items() if
         val == value),
        None
    )


@pytest.fixture(scope="session")
def temp_test_data(tmpdir_factory):
    """
    Fixture (https://docs.pytest.org/en/latest/fixture.html) function to be
    used by the tests.
    This fixture function Creates a valid JSON manifest file in a temporary
    directory. The scope of this fixture is the entire test session.

    :param tmpdir_factory: Fixture used to create temporary directories.
           see: https://docs.pytest.org/en/latest/tmpdir.html#the-tmpdir-factory-fixture
    :return: A dictionary containing these keys:
             'dir': The temporary directory object created by this fixture.
             'json': The created valid manifest JSON file.
             'manifest': The manifest object read from the JSON file.
    """
    test_dir = tmpdir_factory.mktemp('test_data')
    fname = dump_manifest_to_json(manifests[0], 'valid_partition', test_dir)
    valid_manifest = Manifest.from_json(fname)
    return {'dir': test_dir, 'json': fname, 'manifest': valid_manifest}


"""
'modified_json_params' contain the parameters to be used in the 
'modified_json' fixture.
Each key in the dictionary represents a different parameter to be used by 
'modified_json', so for each test which uses
the 'modified_json' fixture, the test will run len(modified_json_params) times,
 each time with different parameters.
Each parameter is a dictionary which contains these keys:
  'partition': A modified partition dictionary.
  'assert': The expected assertion which must occur when running with this 
  parameter.
"""
modified_json_params = {
    'missing_partition_name': {
        'partition': {k: manifests[0][k] for k in manifests[0] if k != 'name'},
        'assert': jexcep.ValidationError
    },
    'missing_partition_id': {
        'partition': {k: manifests[0][k] for k in manifests[0] if k != 'id'},
        'assert': jexcep.ValidationError
    },
    'missing_partition_priority': {
        'partition': {k: manifests[0][k] for k in manifests[0] if
                      k != 'priority'},
        'assert': jexcep.ValidationError
    },
    'missing_entry_point': {
        'partition': {k: manifests[0][k] for k in manifests[0] if
                      k != 'entry_point'},
        'assert': jexcep.ValidationError
    },
    'missing_stack_size': {
        'partition': {k: manifests[0][k] for k in manifests[0] if
                      k != 'stack_size'},
        'assert': jexcep.ValidationError
    },
    'missing_heap_size': {
        'partition': {k: manifests[0][k] for k in manifests[0] if
                      k != 'heap_size'},
        'assert': jexcep.ValidationError
    },
    'missing_source_files': {
        'partition': {k: manifests[0][k] for k in manifests[0] if
                      k != 'source_files'},
        'assert': jexcep.ValidationError
    },
    'missing_irqs_and_sfids': {
        'partition': {k: manifests[0][k] for k in manifests[0] if
                      k not in ['secure_functions', 'irqs']},
        'assert': AssertionError
    },
    'empty_source_files': {
        'partition': dict(manifests[0], source_files=[]),
        'assert': jexcep.ValidationError
    },
    'invalid_minor_policy': {
        'partition': dict(manifests[0],
                          secure_functions=invalid_minor_version_policy_sf),
        'assert': jexcep.ValidationError
    },
    'invalid_nspe_callable': {
        'partition': dict(manifests[0],
                          secure_functions=invalid_nspe_callable_sf),
        'assert': jexcep.ValidationError
    },
    'missing_nspe_callable': {
        'partition': dict(manifests[0],
                          secure_functions=missing_nspe_callable_sf),
        'assert': jexcep.ValidationError
    },
    'invalid_stack_size': {
        'partition': dict(manifests[0], stack_size='str'),
        'assert': jexcep.ValidationError
    },
    'invalid_heap_size': {
        'partition': dict(manifests[0], heap_size='str'),
        'assert': jexcep.ValidationError
    },
    'invalid_priority': {
        'partition': dict(manifests[0], priority='invalid_priority'),
        'assert': jexcep.ValidationError
    },
    'invalid_mmioregion_base': {
        'partition': dict(manifests[0],
                          mmio_regions=[invalid_mmioregion_base]),
        'assert': jexcep.ValidationError
    },
    'invalid_mmioregion_size': {
        'partition': dict(manifests[0],
                          mmio_regions=[invalid_mmioregion_size]),
        'assert': jexcep.ValidationError
    },
    'invalid_irq_num': {
        'partition': dict(manifests[0],
                          irqs=[{"line_num": "str", "signal": "ISR22"}]),
        'assert': jexcep.ValidationError
    },
    'not_exist_src_filename': {
        'partition': dict(manifests[0], source_files=['missing.cpp']),
        'assert': AssertionError
    },
    'invalid_partition_id_decimal': {
        'partition': dict(manifests[0], id=-1),
        'assert': jexcep.ValidationError
    },
    'invalid_partition_id_hex': {
        'partition': dict(manifests[0], id='0xFFFFFFFF'),
        'assert': jexcep.ValidationError
    },
    'duplicates_extern_sfids': {
        'partition': dict(manifests[0], extern_sfids=['SFID66', 'SFID66']),
        'assert': jexcep.ValidationError
    }
}


@pytest.fixture(params=modified_json_params.values(),
                ids=modified_json_params.keys())
def modified_json(request, temp_test_data):
    """
    Fixture (https://docs.pytest.org/en/latest/fixture.html) function to be
    used by the tests.
    This fixture function Creates a JSON manifest file from a given partition
    dictionary and save it
    to a temporary directory.
    This fixture uses the 'temp_test_data' fixture.
    This fixture is a parametrized fixture
    (https://docs.pytest.org/en/latest/fixture.html#parametrizing-fixtures).
    The scope of this fixture is a specific test.

    :param request: Request object which contain the current parameter from
           'modified_json_params'.
    :param temp_test_data: The 'temp_test_data' fixture.
    :return: A list containing these values:
             - The created manifest JSON file for the current parameter.
             - The expected assertion for the current parameter.
    """
    testname = extract_test_name(request.node.name)
    test_file = dump_manifest_to_json(request.param['partition'], testname,
                                      temp_test_data['dir'], False)
    return test_file, request.param['assert']


def test_invalid_json(modified_json):
    """
    Test which gets an invalid JSON manifest file (from the
    'modified_json' fixture) and tries to create a
    Manifest object from it.
    The test expects an assertion to happen.

    :param modified_json: The 'modified_json' fixture.
    :return:
    """
    with pytest.raises(modified_json[1]):
        Manifest.from_json(modified_json[0])


def test_valid_json(temp_test_data):
    """
    Test which gets a valid JSON manifest file (from the 'temp_test_data'
    fixture) and tries to create a Manifest object from it.
    The test expects the Manifest to be same as the Manifest created by the
    'temp_test_data' fixture.

    :param temp_test_data: The 'temp_test_data' fixture.
    :return:
    """
    manifest = Manifest.from_json(temp_test_data['json'])
    assert manifest == temp_test_data['manifest']


# Test parametrization decorator
# See https://docs.pytest.org/en/latest/parametrize.html#pytest-mark-parametrize-parametrizing-test-functions
# Contain the parameters to be used in the 'test_validate_partition_manifest'
# test. It defines a list of (manifest, assertion) tuples which each entry
# will be the input of the 'test_validate_partition_manifest' test, the test
# will run len(LIST_OF_TUPPLES) times, each time with different (manifest,
# assertion) tuple.
# The tuple fields are:
#   'manifest': A modified partition dictionary.
#   'assertion': A tuple containing the expected assertion and assertion
#                string which must occur when running with this parameter.
@pytest.mark.parametrize(
    'manifest, assertion',
    [
        pytest.param(
            dict(manifests[1], name=manifests[0]['name']),
            (ValueError, r'Partition name .* is not unique, .*'),
            id='duplicate_partition_name'
        ),
        pytest.param(
            dict(manifests[1], id=manifests[0]['id']),
            (ValueError, r'Partition id .* is not unique, .*'),
            id='duplicate_partition_id'
        ),
        pytest.param(
            dict(manifests[1],
                 secure_functions=manifests[0]['secure_functions']),
            (ValueError, r'Secure function sfid .* is found in both .*'),
            id='duplicate_sf_sfid'
        ),
        pytest.param(
            dict(manifests[1],
                 secure_functions=duplicate_signal_secure_functions),
            (ValueError, r'Secure function signal .* is found in both .*'),
            id='duplicate_sf_signal'
        ),
        pytest.param(
            dict(manifests[1], irqs=duplicate_signal_irqs),
            (ValueError, r'IRQ signal .* is found in both .*'),
            id='duplicate_irq_signal'
        ),
        pytest.param(
            dict(manifests[1], irqs=duplicate_line_num_irqs),
            (ValueError, r'IRQ line number .* is found in both .*'),
            id='duplicate_irq_line_num'
        ),
        pytest.param(
            dict(manifests[1], extern_sfids=['SFID66', 'SFID999']),
            (
                    ValueError,
                    r'External SFID\(s\) .* can\'t be found in any partition manifest.'
            ),
            id='orphan_extern_ids'
        )
    ]
)
def test_validate_partition_manifest(request, temp_test_data, manifest,
                                     assertion):
    """
    Test which creates an invalid manifest object (after passing JSON schema
    validation) and call
    validate_partition_manifests() with it and with a valid manifest object.
    The test expects an assertion to happen.

    :param request: Request object.
    :param temp_test_data: The 'temp_test_data' fixture.
    :param manifest: The manifest value from the (manifest, assertion) tuple
           for the current parameter.
    :param assertion: The assertion value from the (manifest, assertion) tuple
           for the current parameter.
    :return:
    """
    test_name = extract_test_name(request.node.name)
    test_json = dump_manifest_to_json(manifest, test_name,
                                      temp_test_data['dir'])
    faulty_manifest = Manifest.from_json(test_json)

    with pytest.raises(assertion[0], match=assertion[1]):
        validate_partition_manifests(
            [faulty_manifest, temp_test_data['manifest']])


"""
'verify_json_params' contain the parameters to be used in the 'verify_json' 
fixture. Each key in the dictionary represents a different parameter to be used
by 'verify_json', so for each test which uses the 'verify_json' fixture, the 
test will run len(verify_json_params) times, each time with different 
parameters.
Each parameter is a dictionary which contains these keys:
  'partition': A modified partition dictionary.
  'field': The modified field name.
  'expected': The expected field object.
"""
verify_json_params = {
    'missing_minor_version_secure_functions': {
        'partition': dict(manifests[0],
                          secure_functions=missing_minor_version_sf),
        'field': 'secure_functions',
        'expected': [
            SecureFunction(
                sfid='SFID1', signal='SFID1', minor_policy='relaxed',
                non_secure_clients=True, minor_version=1
            )
        ]
    },
    'missing_minor_version_policy_secure_functions': {
        'partition': dict(manifests[0],
                          secure_functions=missing_minor_version_policy_sf),
        'field': 'secure_functions',
        'expected': [
            SecureFunction(
                sfid='SFID2', signal='SFID2', minor_policy='strict',
                non_secure_clients=True, minor_version=1
            )
        ]
    },
    'missing_minor_completley_secure_functions': {
        'partition': dict(manifests[0],
                          secure_functions=missing_minor_completley_sf),
        'field': 'secure_functions',
        'expected': [
            SecureFunction(
                sfid='SFID2', signal='SFID2', minor_policy='strict',
                non_secure_clients=False, minor_version=1
            )
        ]
    }
}


@pytest.fixture(params=verify_json_params.values(),
                ids=verify_json_params.keys())
def verify_json(request, tmpdir_factory):
    """
    Fixture (https://docs.pytest.org/en/latest/fixture.html) function to be
    used by the tests.
    This fixture function Creates 2 JSON manifest files (The 1st from
    'verify_json_params', the 2nd from manifests[1]) and saves them to a
    temporary directory. This fixture is a parametrized fixture
    (https://docs.pytest.org/en/latest/fixture.html#parametrizing-fixtures).
    The scope of this fixture is a specific test.

    :param request: Request object which contain the current parameter from
           'verify_json_params'.
    :param tmpdir_factory: The 'tmpdir_factory' fixture.
    :return: A dictionary containing these keys:
             'files_list': A list of the created manifest JSON files.
             'field': The changed field in the 1st manifest.
              'expected': The expected 'field' object.
    """
    test_dir = tmpdir_factory.mktemp('test_data')
    test_name = extract_test_name(request.node.name)
    files_list = [
        dump_manifest_to_json(request.param['partition'], '%s1' % test_name,
                              test_dir),
        dump_manifest_to_json(dict(manifests[1], extern_sfids=[]),
                              '%s2' % test_name, test_dir)
    ]
    return {'files_list': files_list, 'field': request.param['field'],
            'expected': request.param['expected']}


def test_verify_json(verify_json):
    """
    Test which gets 2 JSON manifest files (from the 'verify_json' fixture),
    create Manifest objects from them, call validate_partition_manifests() on
    the manifest objects and check that the 1st Manifest object is as expected.

    :param verify_json: The 'verify_json' fixture.
    :return:
    """
    manifest1 = Manifest.from_json(verify_json['files_list'][0])
    manifest2 = Manifest.from_json(verify_json['files_list'][1])

    validate_partition_manifests([manifest1, manifest2])
    assert getattr(manifest1, verify_json['field']) == verify_json['expected']


# Test parametrization decorator
# See https://docs.pytest.org/en/latest/parametrize.html#pytest-mark-parametrize-parametrizing-test-functions
# Contain the parameters to be used in the 'test_is_up_to_date' test.
# It defines a list of (mock_files, expected) tuples which each entry will be
# the input of the 'test_is_up_to_date' test, the test will run
# len(LIST_OF_TUPPLES) times, each time with different (mock_files, expected)
# tuple.
# The tuple fields are:
#   'mock_files': A dictionary to mock file mofied times.
#                 Each entry key is the name of the file and value is it's
#                 modified time.
#   'expected': Expected return value of is_up_to_date() with the
#               given mock_files.
@pytest.mark.parametrize(
    'mock_files, expected',
    [
        pytest.param(test_mock_files, True, id='general'),
        pytest.param(
            {k: test_mock_files for k in test_mock_files if
             not k.startswith('manifest')}, False, id='no_manifest_files'
        ),
        pytest.param(
            {k: test_mock_files for k in test_mock_files if
             not k.startswith('template')}, False, id='no_template_files'
        ),
        pytest.param(
            {k: test_mock_files for k in test_mock_files if
             not k.startswith('gen')}, False, id='no_generated_files'
        ),
        pytest.param(
            dict(test_mock_files, manifest1=max(test_mock_files.values()) + 1),
            False, id='manifest_changed'
        ),
        pytest.param(
            dict(test_mock_files,
                 template_common1=max(test_mock_files.values()) + 1), False,
            id='template_changed'
        )
    ]
)
def test_is_up_to_date(monkeypatch, mock_files, expected):
    """
    Test which calls is_up_to_date() with a given list of files ('mock_files'
    keys) and checks that the return value is same as the 'expected' value.
    The separation of the files in 'mock_files' to (manifest_files,
    template_files, generated_files) is achieved by their name's prefix, for
    example: list of template files is  all the keys in 'mock_files' with 'gen'
    prefix.

    :param monkeypatch: The 'monkeypath' fixture
           (https://docs.pytest.org/en/latest/monkeypatch.html).
    :param mock_files: The mock_files value from the (mock_files, expected)
           tuple for the current parameter.
    :param expected: The expected value from the (mock_files, expected) tuple
           for the current parameter.
    :return:
    """

    def mock_getmtime(mock_file):
        """
        A mocking function for 'os.path.getmtime' which returns the value of
        'test_mock_files[mock-file]'

        :param mock_file: The mocked file name (key in 'test_mock_files').
        :return: The mocked modification-time (value of
                 'test_mock_files[mock-file]').
        """
        return mock_files.get(mock_file, 0)

    monkeypatch.setattr(os.path, 'getmtime', mock_getmtime)

    def get_mock_files(prefix):
        """
        Returns a subset list from 'test_mock_files' with key that starts with
        'prefix'.

        :param prefix: The prefix of the required elements.
        :return: List of elements which match the requirement.
        """
        return {k: mock_files[k] for k in mock_files if k.startswith(prefix)}

    result = is_up_to_date(
        get_mock_files('manifest').keys(),
        get_mock_files('template').keys(),
        get_mock_files('gen').keys()
    )
    assert expected == result


@pytest.fixture(scope="function")
def test_template_setup(tmpdir_factory):
    """
    Fixture (https://docs.pytest.org/en/latest/fixture.html) function to be
    used by the tests. This fixture function Creates JSON manifest files,
    Manifest objects from 'manifest' and template files in a temporary
    directory. The scope of this fixture is the entire test session.

    :param tmpdir_factory: Fixture used to create temporary directories.
           see: https://docs.pytest.org/en/latest/tmpdir.html#the-tmpdir-factory-fixture
    :return: A dictionary containing these keys:
             'dir': The temporary directory object created by this fixture.
             'template_files': List of the created template files.
             'manifest_files': List of the created manifest JSON files.
             'manifests': List of the created Manifest objects.
             'filters': Dictionary with additional filters for
             generate_source_files()
    """

    def find_priority_key(value):
        """
        Finds the key in 'Manifest.PRIORITY' of a given value.

        :param value: The value.
        :return: The key of the given value.
        """
        return next(
            (key for key, val in Manifest.PRIORITY.items() if val == value),
            None)

    def find_permission_key(value):
        """
        Finds the key in 'MmioRegion.MMIO_PERMISIONS' of a given value.

        :param value: The value.
        :return: The key of the given value.
        """
        return next((key for key, val in MmioRegion.MMIO_PERMISSIONS.items() if
                     val == value), None)

    test_dir = tmpdir_factory.mktemp('test_data')
    manifest_files = [
        dump_manifest_to_json(manifest, manifest['name'], test_dir) for
        manifest in manifests]
    manifest_objects = [Manifest.from_json(_file) for _file in manifest_files]
    filters = {
        'basename': os.path.basename,
        'find_priority_key': find_priority_key,
        'find_permission_key': find_permission_key
    }
    template_files = [test_dir.join('_NAME_.json.tpl'),
                      test_dir.join('common.json.tpl')]
    for template, _file in [(test_partition_template, template_files[0]),
                            (test_common_template, template_files[1])]:
        _file.write(template)
    template_files = [_file.strpath for _file in template_files]
    return {
        'dir': test_dir.strpath,
        'template_files': template_files,
        'manifest_files': manifest_files,
        'manifests': manifest_objects,
        'filters': filters
    }


def test_generate_source_files(test_template_setup):
    """
    Test which calls generate_source_files() with the data from
    'test_template_setup' fixture and checks normal output.

    :param test_template_setup: The 'test_template_setup' fixture.
    :return:
    """
    autogen_dir = generate_source_files(
        test_template_setup['manifests'],
        test_template_setup['template_files'],
        test_template_setup['dir'],
        extra_filters=test_template_setup['filters']
    )
    assert os.path.isdir(autogen_dir)

    for gen_file in [os.path.join(autogen_dir, f) for f in
                     os.listdir(autogen_dir)]:
        """
        For each generated json file in 'autogen_dir':
          1. Load the json file to a dictionary named 'generated'.
          2. If it was generated from a partition template ('generated' has a 'name' key):
               a) Read the original manifest json from the test temp dir.
               b) Load the manifest json file to a dictionary named 'expected'.
             Else (generated from a common template):
               a) Calculate 'region_list'.
               b) Build the 'expected' dictionary with values from the original manifest objects.
          3. Compare 'generated' with 'expected'.
        """
        with open(gen_file) as fh:
            generated = json.load(fh)

        if 'name' in generated:
            input_file = os.path.join(test_template_setup['dir'],
                                      generated['name'] + '.json')
            assert os.path.isfile(input_file)
            assert input_file in test_template_setup['manifest_files']
            with open(input_file) as fh:
                expected = json.load(fh)
        else:
            region_list = [region for manifest in
                           test_template_setup['manifests'] for region in
                           manifest.mmio_regions]
            expected = {
                'num_of_partitions': len(test_template_setup['manifests']),
                'partition_names': [manifest.name for manifest in
                                    test_template_setup['manifests']],
                'num_of_region_pairs': len(
                    list(itertools.combinations(region_list, 2)))
            }
        assert generated == expected


def test_process_manifest_files(monkeypatch, test_template_setup):
    """
    Test which calls process_manifest_files() with the data from
    'test_template_setup' fixture.
    Because process_manifest_files() is a compound of the other functions in
    the module which are tested individually, this test just do the following:
    1. Calls process_manifest_files() and checks that the autogen directory
       was created.
    2. Saves the modified times of the generated files.
    3. Calls process_manifest_files() again, checks that the autogen directory
       still exist and that modified times of the generated files didn't
       change.

    :param monkeypatch: The 'monkeypath' fixture
           (https://docs.pytest.org/en/latest/monkeypatch.html).
    :param test_template_setup: The 'test_template_setup' fixture.
    :return:
    """
    monkeypatch.setattr(generate_partition_code, 'TEMPLATES_DIR',
                        test_template_setup['dir'])
    monkeypatch.setitem(DEFAULT_FILTERS, 'basename', os.path.basename)
    monkeypatch.setitem(DEFAULT_FILTERS, 'find_priority_key',
                        find_priority_key)
    monkeypatch.setitem(DEFAULT_FILTERS, 'find_permission_key',
                        find_permission_key)

    autogen_dir = process_manifest_files(test_template_setup['manifest_files'],
                                         test_template_setup['dir'])
    assert os.path.isdir(autogen_dir)

    autogen_files = {}
    for file_name in os.listdir(autogen_dir):
        autogen_files[file_name] = os.path.getmtime(
            os.path.join(autogen_dir, file_name))

    autogen_dir = process_manifest_files(test_template_setup['manifest_files'],
                                         test_template_setup['dir'])
    assert os.path.isdir(autogen_dir)

    for file_name in os.listdir(autogen_dir):
        assert autogen_files[file_name] == os.path.getmtime(
            os.path.join(autogen_dir, file_name))
