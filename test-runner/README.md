# Ansible Solace Test Runner

## Environment

### Mandatory
````bash
export SOLACE_CLOUD_API_TOKEN_RESTRICTED_PERMISSIONS={restricted permissions token}
export SOLACE_CLOUD_API_TOKEN_ALL_PERMISSIONS={all permissions token}
export ANSIBLE_PYTHON_INTERPRETER={python3}
````
### Optional
````bash
export PROJECT_HOME="$GITHUB_WORKSPACE"
export LOG_DIR="$GITHUB_WORKSPACE/${TEST_RUNNER_LOGS_DIR}"
````
## Run

````bash
./run.wf.sh
````

---
The End.
