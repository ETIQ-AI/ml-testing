1. Install Docker [https://docs.docker.com/get-docker/] to your system. You are going to use it to install and run the example.
2. Go to the project directory and run the following command from the terminal: docker-compose up --build
Note:
* to run in daemon mode, run: docker-compose up -d
* to stop the docker later, run:  docker-compose down;
* to rebuild docker image (for example, to get the latest version of the libraries) run:  docker-compose build --no-cache)
3. Open the Airflow user interface in your browser. It will be at the localhost:8080 address.
4. In order to get it to run copy a base dataset (one is provided in the file data/datasets/adult_encoded.csv) file to the data/base directory. Copy a potentially drifted dataset (one is provided in the file data/datasets/adult_encoded_feature_drifted.csv) to the data/latest directory.
 * Find the ‘etiq_drift_example’ DAG and run it.
 * Note that if you have a dashboard you want the results sent to you set the login details in the .env file in the project directory.
