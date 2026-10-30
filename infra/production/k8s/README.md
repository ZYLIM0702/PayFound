# Reference ONLY — Kubernetes is NOT used in the PayFound prototype

Apply only after replacing all placeholder images, container registry, secrets, network
policies, managed PostgreSQL credentials, migrations, TLS, autoscaling metrics and
external provider permissions. This is not a one-command production deployment.

Target future modules: edge/API gateway; commerce API; inventory integration workers;
search indexing; merchant analytics; AI inference. Databases and Kafka should be
managed outside the initial Kubernetes cluster.
