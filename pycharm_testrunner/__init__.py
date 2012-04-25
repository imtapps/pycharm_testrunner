from django.core.exceptions import ImproperlyConfigured
from django.db.models.loading import get_app
from django.test.simple import reorder_suite, DjangoTestSuiteRunner
from django.utils.unittest.case import TestCase
import os
import fnmatch
import re
from django.conf import settings
from unittest.loader import defaultTestLoader
from os.path import dirname

class PyCharmTestSuiteRunner(DjangoTestSuiteRunner):

    def build_suite(self, test_labels, extra_tests=None, **kwargs):
        for label in test_labels:

            if '.' in label:
                parts = label.split('.')
                app = get_project_app(parts[0])
                discovery_root = dirname(app.__file__)
                suite = get_tests(app, parts, discovery_root)
            else:
                app = get_project_app(label)
                app_dir = dirname(app.__file__)
                suite = defaultTestLoader.discover(app_dir, pattern="*test*.py")

        return reorder_suite(suite, (TestCase,))

def build_test_case_path(discovery_root, class_and_method_names, file_path):
    project_path = re.sub(discovery_root, "", file_path)
    module_path = re.sub(".py", "", project_path[1:])
    test_case_path = re.sub(os.sep, '.', module_path)
    if not os.environ.get('TEST_FULL_FILE', None):
        test_case_path += "." + '.'.join(class_and_method_names)
    return test_case_path

def get_py_files(discovery_root):
    for root, _, files in os.walk(discovery_root):
        for filename in fnmatch.filter(files, "*test*.py"):
            yield os.path.join(root, filename)

def get_tests(app, app_label_parts, discovery_root):
    tests = []
    for file_path in get_py_files(discovery_root):
        with open(file_path) as python_file:
            data = python_file.read()
            class_and_method_names = app_label_parts[1:]
            if all([re.search(r"\b{}\b".format(item), data) for item in class_and_method_names]):
                test_case_path = build_test_case_path(discovery_root, class_and_method_names, file_path)
                new_path = '.'.join(app.__name__.split('.')[:-1]) + '.' + test_case_path
                tests.append(defaultTestLoader.loadTestsFromName(new_path))
                break
    return tests

def get_project_apps():
    return [get_project_app(app.split('.')[-1]) for app in settings.PROJECT_APPS]

def get_project_app(app_label):
    for app in settings.PROJECT_APPS:
        if app_label == app.split('.')[-1]:
            break
    else:
        raise ImproperlyConfigured("App with label %s could not be found" % app_label)
    return get_app(app_label)
