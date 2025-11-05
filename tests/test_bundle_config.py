"""Unit tests for Databricks bundle configuration."""
import yaml
import os
import pytest


def test_databricks_yml_exists():
    """Test that databricks.yml exists."""
    assert os.path.exists("databricks.yml"), "databricks.yml not found"


def test_databricks_yml_valid():
    """Test that databricks.yml is valid YAML."""
    try:
        with open("databricks.yml", "r") as f:
            config = yaml.safe_load(f)
            assert config is not None, "databricks.yml is empty"
    except Exception as e:
        pytest.fail(f"Invalid YAML: {e}")


def test_bundle_name_exists():
    """Test that bundle name is defined."""
    with open("databricks.yml", "r") as f:
        config = yaml.safe_load(f)
        assert "bundle" in config, "bundle section not found"
        assert "name" in config["bundle"], "bundle name not found"
        assert config["bundle"]["name"], "bundle name is empty"


def test_environments_defined():
    """Test that at least one environment is defined."""
    with open("databricks.yml", "r") as f:
        config = yaml.safe_load(f)
        assert "environments" in config, "environments section not found"
        assert len(config["environments"]) > 0, "no environments defined"


def test_dev_environment_has_workspace():
    """Test that dev environment has workspace configuration."""
    with open("databricks.yml", "r") as f:
        config = yaml.safe_load(f)
        if "dev" in config.get("environments", {}):
            dev_env = config["environments"]["dev"]
            assert "workspace" in dev_env, "dev environment missing workspace config"
            assert "host" in dev_env["workspace"], "dev workspace missing host"
            assert "root_path" in dev_env["workspace"], "dev workspace missing root_path"


def test_sql_file_exists():
    """Test that SQL file exists."""
    sql_file = "assets/notebooks/transform_data.sql"
    assert os.path.exists(sql_file), f"{sql_file} not found"


def test_sql_file_not_empty():
    """Test that SQL file is not empty."""
    sql_file = "assets/notebooks/transform_data.sql"
    if os.path.exists(sql_file):
        with open(sql_file, "r") as f:
            content = f.read().strip()
            assert len(content) > 0, f"{sql_file} is empty"


def test_warehouse_id_format():
    """Test that warehouse_id is in correct format (not a URL path)."""
    with open("databricks.yml", "r") as f:
        config = yaml.safe_load(f)
        
        # Navigate to warehouse_id in job configuration
        jobs = config.get("resources", {}).get("jobs", {})
        for job_name, job_config in jobs.items():
            tasks = job_config.get("tasks", [])
            for task in tasks:
                sql_task = task.get("sql_task", {})
                if sql_task:
                    warehouse_id = sql_task.get("warehouse_id", "")
                    if warehouse_id:
                        # Should not be a URL path
                        assert not warehouse_id.startswith("/"), \
                            f"warehouse_id '{warehouse_id}' should not start with '/'"
                        assert "?" not in warehouse_id, \
                            f"warehouse_id '{warehouse_id}' should not contain query parameters"
                        assert len(warehouse_id) > 0, \
                            "warehouse_id should not be empty"


def test_sql_task_configuration():
    """Test that SQL task has valid configuration."""
    with open("databricks.yml", "r") as f:
        config = yaml.safe_load(f)
        
        jobs = config.get("resources", {}).get("jobs", {})
        sql_jobs = [job for job in jobs.values() 
                   if any("sql_task" in task for task in job.get("tasks", []))]
        
        assert len(sql_jobs) > 0, "No SQL tasks found in jobs"
        
        for job in sql_jobs:
            for task in job.get("tasks", []):
                sql_task = task.get("sql_task", {})
                if sql_task:
                    # Should have either file or query
                    assert "file" in sql_task or "query" in sql_task, \
                        "SQL task must have either 'file' or 'query'"
                    
                    # If file, should have path
                    if "file" in sql_task:
                        assert "path" in sql_task["file"], \
                            "SQL task file must have 'path'"
                        assert os.path.exists(sql_task["file"]["path"]), \
                            f"SQL file {sql_task['file']['path']} does not exist"
                    
                    # Should have warehouse_id
                    assert "warehouse_id" in sql_task, \
                        "SQL task must have 'warehouse_id'"

