#!/bin/bash

source secret.env

# All Tests
python -m pytest tests/ -v


# Single Files
#python -m pytest tests/test_main.py
#python -m pytest tests/test_helper.py
#python -m pytest tests/test_flow.py -vv

# Single function
#python -m pytest tests/test_flow.py::TestFlow::test_action_start_nip