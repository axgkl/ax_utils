import email.parser
import os

from setuptools import setup
from setuptools import find_packages
from setuptools import Extension


mod1 = Extension(
    "ax_utils.props_to_tree._props_to_tree",
    ["ax_utils/props_to_tree/_props_to_tree.c"],
    extra_compile_args=["-O3"],
)

mod2 = Extension(
    "ax_utils.ax_tree._ax_tree",
    ["ax_utils/ax_tree/_ax_tree.c"],
    extra_compile_args=["-O3"],
)

mod3 = Extension(
    "ax_utils.ax_queue._ax_queue",
    ["ax_utils/ax_queue/_ax_queue.cpp"],
    extra_compile_args=["-O2", "-std=c++11"],
)

mod4 = Extension(
    "ax_utils.unicode_utils._convert_nested",
    ["ax_utils/unicode_utils/_convert_nested.c"],
    extra_compile_args=["-O3"],
)

mod5 = Extension(
    "ax_utils.simple_deepcopy._simple_deepcopy",
    ["ax_utils/simple_deepcopy/_simple_deepcopy.c"],
    extra_compile_args=["-O3"],
)

mod6 = Extension(
    "ax_utils.unicode_utils._isutf8",
    ["ax_utils/unicode_utils/_isutf8.c"],
    extra_compile_args=["-O3"],
)


exts = [mod1, mod2, mod3, mod4, mod5, mod6]
if os.getenv("NO_CPP_EXTENSION"):
    exts.remove(mod3)


def read_version():
    return "3.1.0"


setup(
    name="axiros_utils",
    version=read_version(),
    include_package_data=True,
    ext_modules=exts,
    packages=find_packages(".", include=["ax_utils*"]),
    entry_points={
        "gevent.plugins.monkey.did_patch_all": [
            "ax_queue = ax_utils.ax_queue.gevent_patch:patch"
        ]
    },
)
