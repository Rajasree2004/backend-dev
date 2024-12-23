# tests/testin.py
import json

import pytest
from app import (
    DB_READ_ERROR,
    SUCCESS,
    __app_name__,
    __version__,
    cli,
    todo,
)
from typer.testing import CliRunner

from app import __application__, __version__, cli

runner = CliRunner()

def test_version():
    result = runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert f"{__application__} v{__version__}\n" in result.stdout


@pytest.fixture
def mock_json_file(tmp_path):
    todo = [{"Description": "Get some milk.", "Priority": 2, "Done": False}]
    db_file = tmp_path / "todo.json"
    with db_file.open("w") as db:
        json.dump(todo, db, indent=4)
    return db_file


test_data1 = {
    "description": ["Clean", "the", "house"],
    "priority": 1,
    "todo": {
        "Description": "Clean the house.",
        "Priority": 1,
        "Done": False,
    },
}
test_data2 = {
    "description": ["Wash the car"],
    "priority": 2,
    "todo": {
        "Description": "Wash the car.",
        "Priority": 2,
        "Done": False,
    },
}


@pytest.mark.parametrize(
    "description, priority, expected",
    [
        pytest.param(
            test_data1["description"],
            test_data1["priority"],
            (test_data1["todo"], SUCCESS),
        ),
        pytest.param(
            test_data2["description"],
            test_data2["priority"],
            (test_data2["todo"], SUCCESS),
        ),
    ],
)
def test_add(mock_json_file, description, priority, expected):
    todoer = todo.Todoer(mock_json_file)
    assert todoer.add(description, priority) == expected
    read = todoer._db_handler.read_todos()
    assert len(read.todo_list) == 2


@pytest.fixture
def mock_wrong_json_file(tmp_path):
    db_file = tmp_path / "todo.json"
    return db_file


def test_add_wrong_json_file(mock_wrong_json_file):
    todoer = todo.Todoer(mock_wrong_json_file)
    response = todoer.add(["test task"], 1)
    assert response.error == DB_READ_ERROR
    read = todoer._db_handler.read_todos()
    assert len(read.todo_list) == 0


@pytest.fixture
def mock_wrong_json_format(tmp_path):
    db_file = tmp_path / "todo.json"
    with db_file.open("w") as db:
        db.write("")
    return db_file


def test_add_wrong_json_format(mock_wrong_json_format):
    todoer = todo.Todoer(mock_wrong_json_format)
    assert todoer.add(test_data1["description"], test_data1["priority"]) == (
        test_data1["todo"],
        SUCCESS,
    )
    read = todoer._db_handler.read_todos()
    assert len(read.todo_list) == 1
