
# Documentation 

## Summary
- creates a kubernetes environment with 3 pods, a airflow webserver, a airflow scheduler and a postgres database
- airflow webserver runs a dag, which fetches weather data and pushes it to our database
- the DAG also has a dbt task, which creates custom tables using dbt

## How to run
### create minikube cluster
1.  `minikube start`

2. `minikube mount /Users/aminchoudhury/Desktop/work/weather-api-integration:/data` -> Mounts a local folder into the Minikube VM. You need to keep the tab on, hence the rest of the steps need to be run on a new tab
### build docker images for airflow pds

3. `eval $(minikube docker-env)` -> configures your terminal to use Minikube’s internal Docker daemon, so that any Docker images you build are stored inside Minikube, not your local machine's Docker environment.
4. `docker build -t airflow-webserver:local -f Dockerfile-airflow-webserver .` -> build docker image which will be used by our airflow scheduler and webserver
### create namespaces and deploy kubernetes objects
5. `kubectl create namespace weather-api`
6. 
- `kubectl apply -f kube/postgres.yaml`
- `kubectl apply -f kube/airflow-configmap.yaml`
- `kubectl apply -f kube/airflow-webserver.yaml`
- `kubectl apply -f kube/airflow-scheduler.yaml`
### access airflow UI and tunnel into postgres
7. `kubectl port-forward svc/airflow-webserver 8080:8080`
8. `kubectl port-forward svc/postgres 5432:5432`
### credentials for airflow and postgres
- for postgres, user and password is `admin`
- for postgres, go into Pg Admin, create a server. Port is 5432, username is `admin_username`, password is `admin_password`, db is `staging_db`

## DBT directory format
dbt_project/ 
├── models/
│   ├── staging/                 # Raw sources cleaned and renamed
│   │   └── stg_*.sql
│   ├── intermediate/           # Optional: joins, transformations not ready for final consumption
│   │   └── int_*.sql
│   └── marts/                  # Final models used for BI or end users
│       ├── core/               # Core business entities (e.g., customers, orders)
│       └── reporting/          # Tables for dashboards or reporting tools





